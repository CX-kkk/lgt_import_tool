import json
import pymel.core as pm


# call example
# ijs = ImportJsonShader('/job/HOME/huanggb/working/output2/test.json')
# ijs.import_shader()
class ImportJsonShader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_file(self):
        result = None
        with open(self.file_path, 'r') as f:
            result = f.read()
        return result

    def import_nodes(self, info_mats):
        dic_nodes = {}
        for info_node in info_mats['nodes']:
            name = info_node['name']
            node_type = info_node['type']
            # attrs = info_node['node_attr']

            if node_type == 'shadingEngine':
                node = pm.sets(renderable=1, noSurfaceShader=1, empty=1, name=name)
            elif node_type == 'blinn' or node_type == 'lambert':
                node = pm.shadingNode(node_type, asShader=1, name=name)
            elif node_type == 'bulge':
                node = pm.shadingNode(node_type, at=1, name=name)
            elif node_type == 'place2dTexture':
                node = pm.shadingNode(node_type, au=1, name=name)
            elif node_type == 'file':
                node = pm.shadingNode('file', asTexture=1, isColorManaged=1, name=name)
            elif node_type == 'noise':
                node = pm.shadingNode(node_type, at=1, name=name)
            else:
                node = pm.createNode(node_type, n=name)
            dic_nodes[name] = node
        return dic_nodes

    def handle_plugin_attr(self, attr_name):
        if attr_name.startswith('mi_'):
            if 'Mayatomr' in pm.pluginInfo(q=1, ls=1):
                if not pm.pluginInfo('Mayatomr', q=1, l=1):
                    pm.loadPlugin('Mayatomr', qt=1)
            else:
                return

    def assign_special_node(self, dic_nodes, node, attr_name, attr_value):
        if attr_name == 'animation_curve':
            curve_node = node
            curve_node.setPreInfinityType(attr_value[0])
            curve_node.setPostInfinityType(attr_value[1])
            for idx, value in attr_value[2].items():
                pm.setKeyframe(curve_node, f=value[2], v=value[3], itt=value[0], ott=value[1])
            return True
        if attr_name == 'expression':
            for attr in node.connections(c=1, p=1):
                attr[0].disconnect()
            expression_value = attr_value
            for node_original_name, node_current_name in dic_nodes.items():
                expression_value = expression_value.replace('{}.'.format(node_original_name),
                                                            '{}.'.format(node_current_name.name()))
            pm.expression(node, s=expression_value, ae=1, uc='all', e=1, o="")
            return True

    def assign_attr(self, dic_nodes, name, node_attr, attr_name, attr_value):
        if isinstance(attr_value[1], list):
            if pm.attributeQuery(attr_name, node=dic_nodes[name], nc=1):
                for idx, attr_child in enumerate(node_attr.getChildren()):
                    if attr_child.isLocked() or attr_child.isConnected():
                        return
                    try:
                        attr_child.set(attr_value[1][idx])
                    except:
                        logger.warning('Can not set attribute {} ...'.format(attr_child))
            else:
                logger.warning('{} error ...'.format(node_attr))
        elif isinstance(attr_value[1], dict):
            logger.debug('Attribute {} have a dictionary ...'.format(node_attr))
        else:
            if node_attr.isChild():
                node_attr_parent = node_attr.getParent()
                if node_attr_parent.isLocked() or node_attr_parent.isConnected():
                    return
            try:
                node_attr.set(attr_value[1])
            except:
                logger.warning('Can not set attribute {} ...'.format(node_attr))

    def assign_array(self, node, attr_name, attr_value):
        for attr_arr_idx, attr_arr_value in attr_value[1].items():
            node_attr = node.attr(attr_name.replace('[-1]', '[{}]'.format(attr_arr_idx)))
            if isinstance(attr_arr_value, list):
                for idx, attr_child in enumerate(node_attr.getChildren()):
                    if attr_child.isLocked() or attr_child.isConnected():
                        continue
                    attr_child.set(attr_arr_value[idx])
            else:
                if node_attr.isChild():
                    node_attr_parent = node_attr.getParent()
                    if node_attr_parent.isLocked() or node_attr_parent.isConnected():
                        continue
                node_attr.set(attr_arr_value)

    def assign_coon(self, dic_nodes, node, attr_name, attr_value):
        source_node_name = attr_value[1]
        source_attr_name = attr_value[2]
        if source_node_name in dic_nodes.keys():
            pm.connectAttr('{}.{}'.format(dic_nodes[source_node_name].name(), source_attr_name),
                           '{}.{}'.format(node.name(), attr_name),
                           f=1)
        else:
            pm.connectAttr('{}.{}'.format(source_node_name, source_attr_name),
                           '{}.{}'.format(node.name(), attr_name),
                           f=1)

    def import_connections(self, info_mats, dic_nodes):
        for info_node in info_mats['nodes']:
            name = info_node['name']
            attrs = info_node['node_attr']
            # node_type = info_node['type']
            node = dic_nodes[name]

            for attr_name, attr_value in attrs.iteritems():
                self.handle_plugin_attr(attr_name)

                if self.assign_special_node(dic_nodes, node, attr_name, attr_value):
                    continue

                node_attr = node.attr(attr_name)
                if attr_value[0] == 'value':
                    self.assign_attr(dic_nodes, name, node_attr, attr_name, attr_value)

                if attr_value[0] == 'array':
                    self.assign_array(node, attr_name, attr_value)

                if attr_value[0] == 'conn':
                    self.assign_coon(dic_nodes, node, attr_name, attr_value)

    def check_engine(self, engine):
        result = []
        for obj in engine:
            is_fine = True
            if isinstance(obj, list):
                for item in obj:
                    if not pm.objExists(item):
                        is_fine = False
            else:
                obj_name = obj.split('.')[0]
                is_fine = pm.objExists(obj_name)
            if is_fine:
                result.append(obj)
        return result

    def import_assign(self, info_mats, dic_nodes):
        for sg, engine in info_mats['engines'].iteritems():
            pm.sets(dic_nodes[sg], fe=self.check_engine(engine))

    def import_shader(self):
        info = self.load_file()
        info_mats = json.loads(info)
        dic_nodes = self.import_nodes(info_mats)
        self.import_connections(info_mats, dic_nodes)
        self.import_assign(info_mats, dic_nodes)
