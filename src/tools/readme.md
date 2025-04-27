## Trivial Plan Tools


### 要考虑的事情

首先确定用户的需求

输入信息：
输入信息分为粗粒度和细粒度两方面，粗粒度信息是必须填写的，也就是必填信息，细粒度的可以不填，但填写之后更好，这样的设计有助于用户自主选择。
1. 粗粒度信息
    1. 时空信息：始发地、目的地、出发时间、返程时间
    2. 经济信息：预算信息
    3. 出行目的：比如 我要去趟上海，目的是去开会的，顺便剩下的时间去玩，所以规划就得考虑某段时间是被挤占的
2. 细粒度信息
    1. 交通偏好：拒绝转机/靠窗座位/公共交通vs租车自驾（_这种偏好信息可以用session来存储_） 
        1. 另一类交通便好：经济舱/头等舱，二等票/商务票
    2. 人群属性：亲子行（儿童票/游乐设施）、银发（无障碍通道/慢节奏）、情侣、独行、朋友
    3. 限制条件：饮食禁忌（过敏/长期素食）、宗教信仰（避开某些场所）、运动能力  **多选题**
    4. 旅游倾向：特种兵式旅行、慢节奏享受
    5. 景点倾向：人文情怀、历史古迹、自然冒险、美食打卡、休闲度假、其他（请输入文本）
    6. 预算弹性管理：尽可能花光预算、不强制限制预算、严格控制预算
    


### 工具设计

当用户的规划确定了，那么就可以开始转起来了，需要哪些函数呢？
（增删改查，基本上就只有增（预定）和查两种。当然应该得有个删除...目前应该用不到

0. 计算器：让大模型自己做计算可能会入坑
1. 各类查询 
    1. 航班查询函数：返回某天的航班信息列表。这里做个RAG（用到RAG的地方很多，可以聚合起来）
    2. 火车查询函数：同上，也是RAG
    3. 天气查询函数：查询天气的，避免出现大雨天逛海滩的尴尬情景）
    4. 景区票查询：查看当前景区是否有票，不然没票却在规划里就很傻了。
2. 各类预定
    1. 航班预订
    2. 火车预订
    3. 景区票预订

3. 导航函数？
    1. 这里的设想是直接就生成导航信息，但是这个规划就复杂了，还需要搞一套最短路径，而且还不是点对点的路径，搞不懂。



## Retrieval


### ElasticSearch Server
```shell
# We use Elasticsearch as a vector database to support vector retrieval.

# A simple example to start Elasticsearch using Docker.
# Create a Docker network for network isolation.
docker network create elastic

# Pull the Elasticsearch Docker image.
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.14.3

# Start the Docker container. Note: Set the password as needed.
docker run --name es01 --net elastic -p 9200:9200 -it -m 1GB -e "ELASTIC_PASSWORD=X9y_Z3aB7fC1mD5n" docker.elastic.co/elasticsearch/elasticsearch:8.14.3

# You can write the password into an environment variable.
export ELASTIC_PASSWORD="X9y_Z3aB7fC1mD5n"

# Verify if the startup is successful.
curl --cacert http_ca.crt -u elastic:$ELASTIC_PASSWORD https://localhost:9200
```