CREATE TYPE "public"."animationstatus" AS ENUM('pending', 'processing', 'completed', 'failed');--> statement-breakpoint
CREATE TYPE "public"."messagetype" AS ENUM('user', 'ai');--> statement-breakpoint
CREATE TABLE "messages" (
	"id" text PRIMARY KEY NOT NULL,
	"conversation_id" text NOT NULL,
	"user_id" text NOT NULL,
	"content" text NOT NULL,
	"type" "messagetype" NOT NULL,
	"animation_id" text,
	"created_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "animations" ADD COLUMN "status" "animationstatus" DEFAULT 'pending' NOT NULL;--> statement-breakpoint
ALTER TABLE "animations" ADD COLUMN "progress" text DEFAULT '0.0' NOT NULL;--> statement-breakpoint
ALTER TABLE "animations" ADD COLUMN "status_message" text;--> statement-breakpoint
ALTER TABLE "messages" ADD CONSTRAINT "messages_conversation_id_conversations_id_fk" FOREIGN KEY ("conversation_id") REFERENCES "public"."conversations"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "messages" ADD CONSTRAINT "messages_animation_id_animations_id_fk" FOREIGN KEY ("animation_id") REFERENCES "public"."animations"("id") ON DELETE set null ON UPDATE no action;