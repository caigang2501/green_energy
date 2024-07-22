FROM gp_env1

WORKDIR /green_energy

COPY . .

# COPY requirements.txt .
# RUN pip install -r requirements.txt
# RUN pip install numpy scipy matplotlib pandas tqdm openpyxl

EXPOSE 5000

ENV FLASK_APP=appname.app.py

CMD ["flask", "run", "--host=0.0.0.0"]


# docker build -t green_energy .
# docker save -o green_energy.tar green_energy
# scp danger_env.tar root@10.83.40.175:caigang
# docker load -i green_energy.tar
# docker run -d -p 8088:5000 green_energy


# unzip /tmp/green_energy.zip -d /gcph/pythonData/
# docker run -d -p 8088:5000 --network gp_network green_energy
# docker run -it -p 5010:5000 green_energy bash

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
