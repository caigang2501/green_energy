import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs, make_circles
import networkx as nx
from scipy.spatial.distance import pdist, squareform
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

result_path = ''


def cmeans(data, c, m, max_iter=100, tol=1e-4):
    # 初始化隶属度矩阵
    n = data.shape[0]
    u = np.random.rand(n, c)
    div = np.sum(u, axis=1, keepdims=True)
    u = u / div

    # 迭代更新聚类中心和隶属度
    for _ in range(max_iter):
        # 更新聚类中心
        a = np.dot(u.T**m, data)
        b = np.sum(u**m, axis=0, keepdims=True).T
        centroids = a/b
        
        # 计算距离并更新隶属度
        dist = np.linalg.norm(data[:, None, :] - centroids, axis=2)
        u_new = 1 / np.sum((dist[:,:,None] / dist[:,None,:])**(2/(m-1)), axis=2)
        
        # 计算收敛性
        if np.linalg.norm(u_new - u) < tol:
            break
        
        u = u_new
    
    return centroids, u

# Rc_means

def initialize_membership_matrix(num_data_points, num_clusters):
    U = np.random.rand(num_data_points, num_clusters)
    U = U / np.sum(U, axis=1, keepdims=True)
    return U

def update_cluster_centers(U, data, m):
    centers = []
    for i in range(U.shape[1]):
        numerator = np.sum((U[:, i] ** m)[:, np.newaxis] * data, axis=0)
        denominator = np.sum(U[:, i] ** m)
        centers.append(numerator / denominator)
    return np.array(centers)

def radial_distance(data, center):
    return np.linalg.norm(data - center)

def update_membership_matrix(U, data, centers, m):
    num_clusters = centers.shape[0]
    p = 2 / (m - 1)
    for i in range(U.shape[0]):
        distances = np.array([radial_distance(data[i], centers[j]) for j in range(num_clusters)])
        for j in range(num_clusters):
            if distances[j] == 0:
                U[i, j] = 1
            else:
                denominator = np.sum([(distances[j] / distances[k]) ** p for k in range(num_clusters)])
                U[i, j] = 1 / denominator
    return U

def rc_means(data, num_clusters, m=2, max_iter=100, error=1e-5):
    num_data_points = data.shape[0]
    U = initialize_membership_matrix(num_data_points, num_clusters)
    for iteration in range(max_iter):
        centers = update_cluster_centers(U, data, m)
        U_new = update_membership_matrix(U, data, centers, m)
        if np.linalg.norm(U_new - U) < error:
            break
        U = U_new
    return centers, U

def test_cmeans(data,num_clusters):
    centroids, u = cmeans(data, c=num_clusters, m=2)

    print("聚类中心：")
    print(centroids)

    print("\n隶属度矩阵：")
    print(u)
    # plot_clusters(data, centroids, u, 'clustering_cmeans')
    len_toltal = plot_clusters_with_mst(data, centroids, u, 'clustering_cmeans with MST')
    return len_toltal

def test_rc_means(data,num_clusters):
    centers, U = rc_means(data, num_clusters)

    print("Cluster Centers:\n", centers)
    print("Membership Matrix:\n", U)
    # plot_clusters(data, centers, U, 'clustering_rcmeans')
    len_toltal = plot_clusters_with_mst(data, centers, U, 'clustering_rcmeans with MST')
    return len_toltal

def test_rc_means_zero(data,num_clusters):
    centers, U = rc_means(data, num_clusters)

    print("Cluster Centers:\n", centers)
    print("Membership Matrix:\n", U)
    # plot_clusters(data, centers, U, 'clustering_rcmeans')
    len_toltal = plot_clusters_with_mst1(data, centers, U, 'clustering_rcmeans with MST')
    return len_toltal

def plot_clusters(data, centers, U, title):
    plt.scatter(data[:, 0], data[:, 1], c=np.argmax(U, axis=1), cmap='viridis', marker='o')
    plt.scatter(centers[:, 0], centers[:, 1], c='red', marker='x')
    plt.title(title)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.savefig(result_path+title)
    plt.show()

def plot_clusters_with_mst(data, centers, U, title):
    plt.scatter(data[:, 0], data[:, 1], c=np.argmax(U, axis=1), cmap='viridis', marker='o')
    plt.scatter(centers[:, 0], centers[:, 1], c='red', marker='x')
    plt.title(title)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')

    num_clusters = centers.shape[0]
    labels = np.argmax(U, axis=1)
    total_length = 0  # 初始化总长度

    for cluster in range(num_clusters):
        points = data[labels == cluster]
        if points.shape[0] > 1:  # 至少需要两个点
            graph = nx.Graph()
            for i in range(points.shape[0]):
                for j in range(i + 1, points.shape[0]):
                    distance = np.linalg.norm(points[i] - points[j])
                    graph.add_edge(i, j, weight=distance)
            mst = nx.minimum_spanning_tree(graph)
            for edge in mst.edges(data=True):
                p1, p2 = points[edge[0]], points[edge[1]]
                plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k-', lw=0.5)
                total_length += edge[2]['weight']  

    plt.savefig(result_path+title)
    plt.show()
    return total_length

def plot_clusters_with_mst1(data, centers, U, title):
    plt.scatter(data[:, 0], data[:, 1], c=np.argmax(U, axis=1), cmap='viridis', marker='o')
    plt.scatter(centers[:, 0], centers[:, 1], c='red', marker='x')
    plt.title(title)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')

    num_clusters = centers.shape[0]
    labels = np.argmax(U, axis=1)
    total_length = 0  # 初始化总长度

    for cluster in range(num_clusters):
        labels[0] = cluster
        points = data[labels == cluster]
        if points.shape[0] > 1:  # 至少需要两个点
            graph = nx.Graph()
            for i in range(points.shape[0]):
                for j in range(i + 1, points.shape[0]):
                    distance = np.linalg.norm(points[i] - points[j])
                    graph.add_edge(i, j, weight=distance)
            mst = nx.minimum_spanning_tree(graph)
            
            for edge in mst.edges(data=True):
                p1, p2 = points[edge[0]], points[edge[1]]
                plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k-', lw=0.5)
                total_length += edge[2]['weight'] 


    plt.savefig(result_path+title)
    plt.show()
    return total_length

if __name__=='__main__':
    n_samples = 40
    np.random.seed(41)
    data_normal = np.random.randn(n_samples, 2)
    data_normal[0] = np.array([0,0])
    # data_uniform = np.random.uniform(low=-2, high=2, size=(100, 2))

    data_circular, labels_circular = make_circles(n_samples=n_samples, factor=0.5, noise=0.05)
    data_blob, labels_blob = make_blobs(n_samples=n_samples//3, centers=[(1.5, 1.5)], cluster_std=0.1)
    data_special = np.vstack([data_circular, data_blob])

    len_c = test_cmeans(data_normal,3)
    # len_rc = test_rc_means(data_normal,3)
    len_rc = test_rc_means_zero(data_normal,3)

    print('len_c: ',len_c)
    print('len_rc: ',len_rc)