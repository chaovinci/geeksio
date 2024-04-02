export default incomingMessagesMonitor;
import { Wechaty } from "@juzi/wechaty";
import { createClient, RedisClientType } from "redis";

export async function incomingMessagesMonitor(bot: Wechaty) {
    const redisClient: RedisClientType = createClient({
        url: "redis://127.0.0.1:6379",
    });

    redisClient.on("error", (err) => console.log("Redis Client Error", err));

    redisClient.connect().then(() => console.log("Connected to Redis"));

    while (true) {
        try {
            const result = await redisClient.blPop("sendmsgs", 0);
            console.log("Received message from Redis:", result);

            if (result) {
                const resultAsAny = result as any;

                const messageJson = JSON.parse(resultAsAny.element);

                const { talkerId, text, type } = messageJson;
                const contact = await bot.Contact.find({ id: talkerId });

                if (contact) {
                    await contact.say(`${text}`);
                }
            }
        } catch (e) {
            console.error("Error handling message from Redis:", e);
        }
    }
}
