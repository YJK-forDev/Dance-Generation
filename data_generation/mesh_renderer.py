import pickle
import PIL.Image as pil_img
import os
import numpy as np

### 피클 파일 불러오기 ###
# 1. 피클 파일 경로 설정

# os.environ["PYOPENGL_PLATFORM"] = "osmesa"
import pyrender
import trimesh
# 2. mesh 파일 경로 설정
mesh_dir = "./data/meshes"
file_list_mesh = []

for (root, directories, files) in os.walk(mesh_dir):
    for d in files:
        if d.endswith('.obj'):
            file_list_mesh.append(os.path.join(root, d))

camera_dir = "./data/camera_params"
cam_list = []
for (root, directories, files) in os.walk(camera_dir):
    for d in files:
        if d.endswith('.pkl'):
            d_path = os.path.join(root, d)
            cam_list.append(d_path)
        
file_list_mesh = sorted(file_list_mesh)
cam_list = sorted(cam_list)
print(len(file_list_mesh))

for i in range(len(file_list_mesh)):
    mesh = trimesh.load_mesh(file_list_mesh[i])

    with open(cam_list[i],"rb") as fr:
        data = pickle.load(fr)

    mesh_trimesh, camera_center, camera_transl, focal_length, img_width, img_height = mesh, data['camera_center'], data['camera_transl'], data['focal_length'], data['image_width'], data['image_height']


    material = pyrender.MetallicRoughnessMaterial(
        metallicFactor=0.0,
        alphaMode='OPAQUE',
        baseColorFactor=(1.0, 1.0, 0.9, 1.0))

    # script_dir = os.path.dirname(os.path.realpath(__file__))
    vertex_colors = np.loadtxt(os.path.join('./data/smplx_verts_colors.txt'))
    mesh_new = trimesh.Trimesh(vertices=mesh_trimesh.vertices, faces=mesh_trimesh.faces, vertex_colors=vertex_colors)
    mesh_new.vertex_colors = vertex_colors
    print("mesh projectioning number : ", i)

    #mesh = pyrender.Mesh.from_points(out_mesh.vertices, colors=vertex_colors)

    mesh = pyrender.Mesh.from_trimesh(mesh_new, smooth=False, wireframe=False)

    scene = pyrender.Scene(bg_color=[1.0, 1.0, 1.0],
                            ambient_light=(0.3, 0.3, 0.3))
    #scene = pyrender.Scene(bg_color=[0.0, 0.0, 0.0, 0.0])
    scene.add(mesh, 'mesh')

    camera_pose = np.eye(4)
    camera_pose[:3, 3] = camera_transl

    camera = pyrender.camera.IntrinsicsCamera(
        fx=focal_length, fy=focal_length,
        cx=camera_center[0], cy=camera_center[1])
    scene.add(camera, pose=camera_pose)

    light = pyrender.light.DirectionalLight()

    scene.add(light)
    r = pyrender.OffscreenRenderer(viewport_width=img_width,
                                    viewport_height=img_height,
                                    point_size=1.0)
    color, _ = r.render(scene, flags=pyrender.RenderFlags.RGBA)
    color = color.astype(np.float32) / 255.0

    output_img = color[:, :, 0:3]
    output_img = (output_img * 255).astype(np.uint8)

    output_img = pil_img.fromarray(output_img)
    #out_img_save_path = os.path.join(save_dir_results, '000001.png' % fid)
    
    # 3. 렌더링된 png가 저장될 경로 설정
    save_smpl_params = os.path.join("./data/rendered_smplifyx_meshes/", file_list_mesh[i].split("/")[-2])

    os.makedirs(save_smpl_params, exist_ok=True)

    save_name = file_list_mesh[i].split("/")[-1].split(".")[0] + ".png"

    output_img.save(os.path.join(save_smpl_params, save_name))
    #print("saved rendered mesh to %s" % out_img_save_path)

