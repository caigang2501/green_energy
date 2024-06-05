# 使用一个基础的 Python 镜像
FROM green_eng

# 设置工作目录
WORKDIR /green_energy
# 复制当前目录下的所有文件到工作目录
COPY . .

# 安装依赖
#RUN pip install --ignore-installed -r requirements.txt
# RUN pip install -r requirements.txt
# RUN chmod 644 /data

# 暴露服务运行的端口
EXPOSE 5000

# 定义环境变量
ENV FLASK_APP=appname.app.py

# 运行 Flask 服务
CMD ["flask", "run", "--host=0.0.0.0"]


# docker build -t danger_dtc1 .
# docker save -o danger_env.tar danger_dtc_env
# scp danger_env.tar root@10.83.40.175:caigang
# docker load -i danger_dtc.tar
# docker run -d -p 8088:5000 danger_dtc1
# docker run -it -p 5010:5000 danger_dtc bash

# docker exec -it <e2545f0769ed> uname -m
# gunicorn -w 4 -b 0.0.0.0:5000 your_flask_app:app
# uwsgi --http :5000 --wsgi-file your_flask_app.py

#删除指定容器
#docker rm <container_id_or_name>
#删除所有停止的容器
#docker container prune
#删除指定镜像
#docker rmi <image_id_or_name>
#删除所有未被使用的镜像
#docker image prune
## 删除所有容器
#docker rm $(docker ps -aq)
## 删除所有镜像
#docker rmi $(docker images -q)
