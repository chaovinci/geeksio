# geeksio
Geek's io 帮你处理微信的消息收发，微信就是你的io，而你就专注于给自己的助理增加新功能了。
另外分享大家做的助理，让大家可以直接使用，不用再重复造轮子了。

首先添加 Geek's io 好友：

## <img src="https://github.com/chaovinci/geeksio/blob/main/geeksio_qrcode.png" height="56"/>

你发送的消息，会被转发到你的hook 地址

你处理处理完后，将回复信息发送到 https://msg.io.sapling.pro
```
curl -X POST -H "Content-Type: application/json" -d '{"text":"yourmessage", "token": "yourtoken"}' https://msg.io.sapling.pro

```


发送消息

.hook https://yourhookurl
设置你的服务器 hook 地址

.token
更新你的 token，旧 token 将立即失效


### 为什么做这个？
我希望做一个微信的个人助理，然后尝试了各种不同的 bot 程序，部署太过于麻烦，稳定性也不好。
我只是想要一个简单的个人 bot，而不是构建一个为其他人服务器的 bot。
其他人肯定也遇到这种情况，所以我就做了这个，这样你就不用再做一遍了。