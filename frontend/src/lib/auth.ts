import { db } from "@/db/drizzle";
import { account, session, user, verification } from "@/db/schema";
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
 
export const auth = betterAuth({
    socialProviders: {
        google: {
            clientId: process.env.GOOGLE_CLIENT_ID as string,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET as string,
            prompt: "select_account",
        },
    },
    database: drizzleAdapter(db, {
        provider: "pg", 
        schema: {
            user,
            account,
            session,
            verification
        }
    }),
    emailAndPassword: {  
        enabled: true
    },
    // socialProviders: { 
    //     github: { 
    //        clientId: process.env.GITHUB_CLIENT_ID as string, 
    //        clientSecret: process.env.GITHUB_CLIENT_SECRET as string, 
    //     }, 
    // }, 
});