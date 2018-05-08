import json
import maya.cmds as mc
import pymel.core as pm

EXPORT_USER_ATTR = True


# call example
# export_json('/job/HOME/huanggb/working/output2/test.json')
class ShadingObject(object):
    @staticmethod
    def split_object_faces(mesh_face):
        face_string = str(mesh_face)
        result = []
        if ',' in face_string:
            faces_split = face_string.split('[')
            head = faces_split[0]
            faces_items = faces_split[1].split(']')[0]
            for item in faces_items.split(','):
                split_item = item.split(':')
                if len(split_item) == 3:
                    for x in range(int(split_item[0]), int(split_item[1]) + 1, int(split_item[2])):
                        result.append('{}[{}]'.format(head, x))
                else:
                    result.append('{}[{}]'.format(head, item))
        else:
            result.append(face_string)
        return result

    @classmethod
    def get_engines(cls):
        engines = {}
        shading_engines = pm.ls(type='shadingEngine')

        for engine in shading_engines:
            assign_dest = engine.asSelectionSet()
            if len(assign_dest) == 0:
                continue

            engines[engine.longName()] = [cls.split_object_faces(n) for n in assign_dest
                                          if pm.objExists(str(n).split('.')[0])]
        return engines


class Node:
    def __init__(self, name, nodes, ident=0):
        self.name = name
        self.node = pm.PyNode(name)
        self.node_type = self.node.nodeType()
        self.attr = {}
        self.nodes = nodes
        self.nodes[self.name] = self
        self.ident = ident

    def if_attribute_needed(self, node, attr_long_name):
        if 'message' == attr_long_name:
            return False

        bad_conn_attribute = ['ObjectGroups', 'objectGroups', 'instObjGroups', 'partition', 'objectMsg']
        for attr_bad in bad_conn_attribute:
            if attr_bad in attr_long_name:
                return False

        if node in ['defaultColorMgtGlobals']:
            return False
        return True

    def node_create_type_filter(self, node):
        node_type = None
        if isinstance(node, unicode):
            node_type = mc.nodeType(node)
        else:
            node_type = node.type()
        return node_type not in ['transform',
                                 'colorManagementGlobals',
                                 'time',
                                 'renderGlobals',
                                 'renderLayer',
                                 'reference']

    def build_connect_attr(self):
        connections = mc.listConnections(self.node.name(), plugs=True, source=True, destination=False, c=1) or []
        for i in xrange(0, len(connections), 2):
            source_attr = connections[i + 1]
            backward_attr = connections[i]

            source_split = source_attr.split('.')
            source_node = source_split[0]
            source_long_name = '.'.join(source_split[1:])

            backward_split = backward_attr.split('.')
            backward_long_name = '.'.join(backward_split[1:])

            if not self.if_attribute_needed(source_node, source_long_name):
                continue

            if self.node_create_type_filter(source_node) and source_node not in self.nodes.keys():
                conn_node = Node(source_node, self.nodes, self.ident + 1)
                conn_node.walk_connections()

            self.attr[backward_long_name] = ['conn', source_node, source_long_name]

    def get_array_attr(self, attr_name_split):
        inputs_attr = self.node.attr(attr_name_split[0])
        dic_value = {}
        for idx in inputs_attr.getArrayIndices():
            dic_value[idx] = inputs_attr.elementByLogicalIndex(idx).attr(attr_name_split[-1]).get()
        if len(dic_value) > 0:
            current_attr_name = '{}[-1].{}'.format(attr_name_split[0], attr_name_split[1])
            self.attr[current_attr_name] = ['array', dic_value]

    def get_attr(self, attr_name):
        node_attr = self.node.attr(attr_name)
        if node_attr.isArray():
            return

        if not EXPORT_USER_ATTR:
            if node_attr in self.node.listAttr(ud=True):
                return

        if node_attr.isMulti():
            for element in node_attr.elements():
                if element in self.attr.keys():
                    return

                element_attr = self.node.attr(element)
                attr_value = element_attr.get()
                if attr_value is not None:
                    self.attr[element] = ['value', attr_value]
        else:
            attr_value = node_attr.get()
            if attr_value is not None:
                self.attr[attr_name] = ['value', attr_value]

    def list_attribute_special_nodes(self):
        if self.node.type() == 'animCurveUU':
            curve_node = self.node
            dic_value = {}
            for idx in xrange(curve_node.numKeys()):
                array_value = [curve_node.getInTangentType(idx).key,
                               curve_node.getOutTangentType(idx).key,
                               curve_node.getUnitlessInput(idx),
                               curve_node.getValue(idx)]
                dic_value[idx] = array_value
            if dic_value:
                attr = [curve_node.getPreInfinityType().index, curve_node.getPostInfinityType().index, dic_value]
                self.attr['animation_curve'] = attr
            return True
        if self.node.type() == 'expression':
            self.attr['expression'] = self.node.attr('expression').get()
            return True
        return False

    def list_attribute_normal_nodes(self):
        # self.node.listAttr() -> mc.listAttr(self.node.name())
        for attr_name in mc.listAttr(self.node.name()):  # , v=1, iu=1
            if not self.if_attribute_needed(self.node, attr_name):
                continue

            if attr_name in self.attr.keys():
                continue

            attr_name_split = attr_name.split('.')

            # remove hasAttr
            if len(attr_name_split) > 1:
                self.get_array_attr(attr_name_split)
            else:
                self.get_attr(attr_name)

    def walk_connections(self):
        self.build_connect_attr()

        if self.list_attribute_special_nodes():
            return

        self.list_attribute_normal_nodes()

    def walk_attrs(self):
        for attr in self.node.listAttr(r=1, w=1, sa=1, c=1):
            attr_name = attr.longName()
            if attr.isDestination():
                conn = attr.listConnections(plugs=True, d=False)[0]
                conn_node_name = conn.node().longName()
                if conn_node_name not in self.nodes.keys():
                    conn_node = Node(conn_node_name, self.nodes)
                    conn_node.walk_attrs()
                self.attr[attr_name] = ['conn', conn_node_name, conn.longName()]
            else:
                value = attr.get()
                self.attr[attr_name] = ['value', value]

    def __str__(self):
        return 'name:{}, type:{}, attr:{}'.format(self.name, self.node_type, self.attr)

    @staticmethod
    def build_shading_nodes(shading_nodes=None, is_attr=False):
        shading_engines = shading_nodes or [n.name() for n in pm.ls(type='shadingEngine')]

        nodes = {}
        for shading_engine in shading_engines:
            n = Node(shading_engine, nodes)
            if is_attr:
                n.walk_attrs()
            else:
                n.walk_connections()
        return nodes.values()


def get_output():
    engines = ShadingObject.get_engines()
    nodes = Node.build_shading_nodes(engines.keys())
    return {'engines': engines, 'nodes': nodes}


def node_encoder(obj):
    if isinstance(obj, Node):
        translate_dic = {'name': obj.name, 'type': obj.node_type, 'node_attr': obj.attr}
        return translate_dic
    if isinstance(obj, pm.datatypes.Matrix):
        return {'matrix': obj.get()}
    if isinstance(obj, pm.datatypes.Vector):
        return {'vector': obj.get()}
    return json.JSONEncoder().default(obj)


def export_json(file_path, export_user_attr=False):
    global EXPORT_USER_ATTR
    EXPORT_USER_ATTR = export_user_attr
    with open(file_path, 'w+') as f:
        dic = get_output()
        d = json.dumps(dic, indent=4, sort_keys=True, default=node_encoder)
        f.write(d)
