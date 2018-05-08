import json
import maya.cmds as cmds
import pymel.core as pm
import core.import_shading_group as isg


def check_engine(engine, namespace=''):
    result = []
    for obj in engine:
        if isinstance(obj, list):
            for item in obj:
                np_item = '{}:{}'.format(namespace, item.replace('|', '|{}:'.format(namespace)))
                if pm.objExists(np_item):
                    result.append(np_item)
                else:
                    print np_item
        else:
            obj_name = obj.split('.')[0]
            obj_np = '{}:{}'.format(namespace, obj_name.replace('|', '|{}:'.format(namespace)))
            if pm.objExists(obj_np):
                result.append(obj_np)
            else:
                print obj_np
    return result


def import_nodes(info_mats, renaming_prefix):
    dic_nodes = {}
    for info_node in info_mats['nodes']:
        name = info_node['name']
        node = pm.PyNode('{}_{}'.format(renaming_prefix, name))
        dic_nodes['{}_{}'.format(renaming_prefix, name)] = node
    return dic_nodes


def import_assign(info_mats, dic_nodes, namespace=''):
    for sg, engine in info_mats['engines'].iteritems():
        print sg, engine
        fe = check_engine(engine, namespace=namespace)
        pm.sets(dic_nodes['{}_{}'.format(namespace, sg)], fe=fe)


def import_shader(shader_path, renaming_prefix):
    # cmds.file(shader_path, i=True, type="mayaBinary", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False,rpr=renaming_prefix, options="v=0;", pr=True)
    cmds.file(shader_path, i=True, type="mayaAscii", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False,
              rpr=renaming_prefix, options="v=0;", pr=True)


def main(abc_path, json_path, shader_path, namespace, load_abc=True, load_texture=True):
    # reference abc
    if load_abc:
        cmds.file(abc_path, r=True, type="Alembic", ignoreVersion=True, gl=True, mergeNamespacesOnClash=False,
                  namespace=namespace)
    if load_texture:
        # import json
        ijs = isg.ImportJsonShader(json_path)
        info = ijs.load_file()
        info_mats = json.loads(info)
        # import shader
        import_shader(shader_path, namespace)
        dic_nodes = import_nodes(info_mats, namespace)
        import_assign(info_mats, dic_nodes, namespace=namespace)


if __name__ == '__main__':
    shader_path = '/show/BRI/shot/z_dev/testShot/ani/work/pletest/maya/scenes/hz/test/ex_shd/shaders.ma'
    abc_path = "/show/BRI/shot/z_dev/testShot/ani/work/pletest/maya/scenes/hz/test/ex_shd/aa.abc"
    json_path = '/show/BRI/shot/z_dev/testShot/ani/work/pletest/maya/scenes/hz/test/ex_shd/shader.json'
    namespace = 'aa'
    main(abc_path, json_path, namespace)


