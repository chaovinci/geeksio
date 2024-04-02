import { Message } from "@juzi/wechaty";
import { RedisClientType } from "redis";

enum MessageType {
    Unknown = 0,
    Attachment = 1, // Attach(6),
    Audio = 2, // Audio(1), Voice(34)
    Contact = 3, // ShareCard(42)
    ChatHistory = 4, // ChatHistory(19)
    Emoticon = 5, // Sticker: Emoticon(15), Emoticon(47)
    Image = 6, // Img(2), Image(3)
    Text = 7, // Text(1)
    Location = 8, // Location(48)
    MiniProgram = 9, // MiniProgram(33)
    GroupNote = 10, // GroupNote(53)
    Transfer = 11, // Transfers(2000)
    RedEnvelope = 12, // RedEnvelopes(2001)
    Recalled = 13, // Recalled(10002)
    Url = 14, // Url(5)
    Video = 15, // Video(4), Video(43)
    Post = 16, // Moment, Channel, Tweet, etc
}

export class TransmitMessageToConsumer {
    async onMessage(message: Message, redisClient: RedisClientType) {
        const talker = message.talker();
        const rawText = message.text();

        // 不处理群消息
        const room = message.room()
        if (room) {
            return;
        }

        // 用于测试连通性
        if (rawText.startsWith("/ping")) {
            await message.say("pong");
        }
        
        // 这些消息类型还有很多其他的属性，可以根据需要进行处理
        let content = {}
        console.log("message.type()", message.type());

        if (message.type() == MessageType.Location) {
            const location = await message.toLocation();
            content = {
                'name': location.name(),
                'address': location.address(),
                'latitude': location.latitude(),
                'longitude': location.longitude(),
                'accuracy': location.accuracy(),
            }
            console.log("message.toLocation()", content);
        }

        if (message.type() == MessageType.MiniProgram) {
            const miniProgram = await message.toMiniProgram();
            content = {
                'appid': miniProgram.appid(),
                'description': miniProgram.description(),
                'pagePath': miniProgram.pagePath(),
                'thumbKey': miniProgram.thumbKey(),
                'thumbUrl': miniProgram.thumbUrl(),
                'title': miniProgram.title(),
                'username': miniProgram.username(),
            }
        }

        if (message.type() == MessageType.Url) {
            const url = await message.toUrlLink();
            content = {
                'description': url.description(),
                'thumbnailUrl': url.thumbnailUrl(),
                'title': url.title(),
                'url': url.url(),
            }
        }
            
        // Attachment-1, Audio-2,  Emoticon-5, Image-6, Video-15
        const FileMessageType = [1, 2, 5, 6, 15];
        let filePath = "";

        if (FileMessageType.includes(message.type())) {
            try {
                const fileBox = await message.toFileBox();
                filePath = "./files/" + fileBox.name;

                await fileBox.toFile(filePath, true);
                console.log("File saved successfully", filePath);
            } catch (e) {
                filePath = "";
                console.log("Failed to save file", e);
            }
        }

        const talkerName = talker.name();

        const messageWithTalkerNameAndFilePath = {
            ...message,
            talkerName,
            filePath,
            content,
        };

        const redisRes = await redisClient.lPush(
            "messages",
            JSON.stringify(messageWithTalkerNameAndFilePath)
        );
        const msgRes = await redisClient.lPush(
            "msg",
            JSON.stringify(messageWithTalkerNameAndFilePath)
        );
        console.log(`Added to queue messages redisRes: ${redisRes}`);
        console.log(`Added to queue msg msgRes: ${msgRes}`);

        return;
    }
}

