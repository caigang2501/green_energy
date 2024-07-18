echo "开始获取容器的id"
# 获取容器的id
cid=`docker ps | grep gcph | awk '{print $1}'`

echo ${cid}

# 停止并删除容器
docker stop ${cid}
docker rm ${cid}
echo "停止并删除容器" ${cid}

# 镜像打包
echo "镜像打包中....."
cd /gcph/project/
docker build -t gcph:1.0.0 .

sleep 20s
# 获取 项目 镜像id
cfnid=`docker images | grep gcph  | awk '{print $3}'`
echo "获取app镜像id" ${cfnid}

# 启动镜像
docker run --name gcph -p 9999:9999 -d ${cfnid}
echo "success!启动gcph镜像完成"