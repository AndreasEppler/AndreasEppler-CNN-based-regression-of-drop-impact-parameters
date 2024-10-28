import matplotlib.pyplot as plt
import numpy as np
import os
from os import walk
import trimesh
import math
import json
from skimage.measure import EllipseModel
from matplotlib.patches import Ellipse
from scipy.spatial import ConvexHull
from scipy.stats import moment

def calc_Vol_Area_Centroid(path):
    'This method calculates the Volume and Surface area of a mesh'
    mesh = trimesh.load_mesh(path)
    V = mesh.volume
    A = mesh.area
    C = mesh.centroid
    return V, A, C

def calc_angles(path):
    'This method loads a droplet mesh and calculates the contact angles around the perimeter of the contact line'
    mesh = trimesh.load(path)
    plane_normal = (0,-1,0)
    plane_origin = (0,1.2,0)
    bottom_mesh = trimesh.intersections.slice_mesh_plane(mesh, plane_normal, plane_origin)

    plane_normal = (0, 1, 0)
    plane_origin = (0, 1.0, 0)
    middle_mesh = trimesh.intersections.slice_mesh_plane(bottom_mesh, plane_normal, plane_origin)
    
    verts = middle_mesh.vertices
    normals = middle_mesh.face_normals
    angles = []
    for n in normals:
        pair = np.stack((n, plane_normal), axis=1)
        pair = pair.T
        pair = np.expand_dims(pair, axis=0)
        angle = trimesh.geometry.vector_angle(pair)
        angles.append(angle)
    angles = np.squeeze(angles)
    elevation = angles * 180 / math.pi
    return elevation

def get_bottom_sliced_area_scatter(path):
    mesh = trimesh.load(path)
    isect, face_inds = trimesh.intersections.mesh_plane(
        mesh,
        plane_normal=(0,1,0),
        plane_origin=(0,1.0,0),
        return_faces=True
        )
    bottom_area_coordinates=np.array(isect[:,0,0::2])
    return bottom_area_coordinates

# Sorts coordinates clockwise
# Only works if center is (0, 0)
def sort_clockwise(coords):
   # coords is a numpy array of shape (2, n) where n is the number of coordinates
   angles = np.arctan2(coords[:,0], coords[:,1]) # calculate angles
   sorted_indices = np.argsort(angles) # sort indices by angles
   return coords[sorted_indices] # return sorted coordinates

# This function calculates the area of a polygon given its vertices based on the so-called
# Shoelace-Formula
# ! The coordinates must be sorted either in a clockwise - or counterclockwise manner.
def polygon_area(coords):
    # coords is a numpy array of shape (2, n) where n is the number of vertices
    x = coords[:,0]
    y = coords[:,1]
    area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
    return area

# Define a function to calculate the circumference of a polygon
def circumference(coords):
    # coords is a numpy array of shape (2, n) where n is the number of vertices
    x = coords[:,0]
    y = coords[:,1]
    # Initialize the circumference to zero
    c = 0
    # Loop through the vertices of the polygon
    for i in range(len(x)):
        # Get the coordinates of the current and next vertex
        x1, y1 = x[i], y[i]
        x2, y2 = x[(i + 1) % len(x)], y[(i + 1) % len(y)]
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # Add the distance between them to the circumference
        c += distance
    # Return the circumference
    return c

##roughness parameters

def get_a(bottom_area_coordinates):
    radius=0
    center=[0,0]
    intersects=False
    while intersects is False:
        radius+=0.1
        for i in range(0,len(bottom_area_coordinates)):
            if (np.linalg.norm(bottom_area_coordinates[i]-center)<= radius):
                intersects=True
                radius-=0.1
                break
    a=[]           
    for i in range(0,len(bottom_area_coordinates)):
            a.append((np.linalg.norm(bottom_area_coordinates[i]-center)-radius))
    return np.array(a)

def get_w_of_a(a):
    return np.sqrt(1/len(a)*np.sum((a-np.mean(a))**2))

def get_root_mean_square_height(a):
    return np.sqrt(1/len(a)*np.sum(a**2))

def get_skewness(a):
    rmsh=get_root_mean_square_height(a)
    return 1/(len(a)*rmsh**3)*np.sum(a**3)

def get_kurtosis(a):
    rmsh=get_root_mean_square_height(a)
    return 1/(len(a)*rmsh**4)*np.sum(a**4)

def get_max_pit_height(a):
    mean=np.mean(a)
    sv=abs(np.min(a)-mean)
    return sv

def get_max_peak_height(a):
    mean=np.mean(a)
    sp=np.max(a)-mean
    return sp

def get_ellipsis_parameters(coordinates):
    x = coordinates[:, 0]
    y = coordinates[:, 1]
    ell = EllipseModel()
    ell.estimate(coordinates)
    xc, yc, a, b, theta = ell.params
    return a/b, theta

def get_point_aspect_ratio(coordinates):
    distance = np.zeros(len(coordinates))
    for i in range(len(distance)):
        distance[i] = np.sqrt(coordinates[i,0]**2+coordinates[i,1]**2)
    a1 = np.max(distance)
    a2 = np.min(distance)
    return a1/a2

def get_hull_ratio(coords):
    hull = ConvexHull(coords)    
    hull_data = coords[hull.vertices]
    sorted_coords = sort_clockwise(coords)
    shadowed_area = polygon_area(sorted_coords)
    sorted_coords_hull = sort_clockwise(hull_data)
    shadowed_area_hull = polygon_area(sorted_coords_hull)
    return shadowed_area/shadowed_area_hull

def get_central_moments(coords,order):
    return moment(coords, moment=order)

def createJson(filename, name, data):
    # create dictionary
    dataDict = {}
    for i in range(len(name)):
        dataDict[name[i]] = list(data[i,:])
    # write to file
    with open(filename+'.json', 'w') as f:
        json.dump(dataDict, f)
    return dataDict

if __name__ == "__main__":
    obj_path ='/pfs/work7/workspace/scratch/oy0026-DDE2_droplet/OBJ/'

    filenames = []
    for (dirpath, dirnames, file_name) in walk(obj_path):
        for dirname in dirnames:
            for (dirpath, dirnames, file_name) in walk(obj_path+dirname):
                filenames.append(os.path.join(obj_path,dirname+'/'+file_name[0]))
        break
    filenames = sorted(filenames)
    
    volume = []
    surface_area = []
    centroid = []
    contact_angle = []
    
    shadowed_area = []
    perimeter = []
    
    w = []
    skewness = []
    kurtosis = []
    max_pit_height = []
    max_peak_height = []

    aspect_ratio = []
    theta = []
    point_aspect_ratio = []
    hull_ratio = []
    
    moment2=[]
    moment3=[]
    moment4=[]
    
    for subject_path in filenames:
        if subject_path.endswith('.obj'):
            #standard parameters
            Vol, Ar, C = calc_Vol_Area_Centroid(subject_path)
            volume.append(Vol)
            surface_area.append(Ar)
            centroid.append(C)
            angles=calc_angles(subject_path)
            if len(angles)==0:
                contact_angle.append(math.nan)
            else:
                contact_angle.append(np.mean(calc_angles(subject_path)))
            
            coords = get_bottom_sliced_area_scatter(subject_path)

            #roughness parameters
            if len(coords) == 0:
                shadowed_area.append(math.nan)
                perimeter.append(math.nan)
                w.append(math.nan)
                skewness.append(math.nan)
                kurtosis.append(math.nan)
                max_pit_height.append(math.nan)
                max_peak_height.append(math.nan)
                aspect_ratio.append(math.nan)
                theta.append(math.nan)
                point_aspect_ratio.append(math.nan)
                hull_ratio.append(math.nan)
                moment2.append([math.nan,math.nan])
                moment3.append([math.nan,math.nan])
                moment4.append([math.nan,math.nan])
            else: 
                sorted_coords = sort_clockwise(coords)
                shadowed_area.append(polygon_area(sorted_coords))
                perimeter.append(circumference(sorted_coords))
                
                a = get_a(coords)
                w.append(get_w_of_a(a))
                skewness.append(get_skewness(a))
                kurtosis.append(get_kurtosis(a))
                max_pit_height.append(get_max_pit_height(a))
                max_peak_height.append(get_max_peak_height(a))
                #ellipsis
                ar,t=get_ellipsis_parameters(coords)
                aspect_ratio.append(ar)
                theta.append(t)
                point_aspect_ratio.append(get_point_aspect_ratio(coords))
                hull_ratio.append(get_hull_ratio(coords))
                moment2.append(get_central_moments(coords,2))
                moment3.append(get_central_moments(coords,3))
                moment4.append(get_central_moments(coords,4))
                
    volume = np.array(volume)
    surface_area = np.array(surface_area)
    centroid = np.array(centroid)
    contact_angle = np.array(contact_angle)
    
    shadowed_area = np.array(shadowed_area)
    perimeter = np.array(perimeter)
    
    w = np.array(w)
    skewness = np.array(skewness)
    kurtosis = np.array(kurtosis)
    max_pit_height = np.array(max_pit_height)
    max_peak_height = np.array(max_peak_height)

    aspect_ratio = np.array(aspect_ratio)
    theta = np.array(theta)
    point_aspect_ratio = np.array(point_aspect_ratio)
    hull_ratio = np.array(hull_ratio)
    moment2=np.array(moment2)
    moment3=np.array(moment3)
    moment4=np.array(moment4)
    
    dataDict = createJson('parameter_data',filenames,np.vstack((volume,surface_area,centroid[:,0],centroid[:,1],centroid[:,2],contact_angle,shadowed_area, perimeter, w,skewness,kurtosis,max_peak_height,max_pit_height,aspect_ratio,theta,point_aspect_ratio,hull_ratio,moment2[:,0],moment2[:,1],moment3[:,0],moment3[:,1],moment4[:,0],moment4[:,1])).T)