-- Create message type enum if it doesn't exist
DO $$ BEGIN
  CREATE TYPE "messagetype" AS ENUM ('user', 'ai');
EXCEPTION
  WHEN duplicate_object THEN
    NULL;
END $$;

-- Create messages table
CREATE TABLE IF NOT EXISTS "messages" (
  "id" text PRIMARY KEY NOT NULL,
  "conversation_id" text NOT NULL,
  "user_id" text NOT NULL,
  "content" text NOT NULL,
  "type" "messagetype" NOT NULL,
  "animation_id" text,
  "created_at" timestamp DEFAULT now() NOT NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS "idx_messages_conversation_id" ON "messages" ("conversation_id");
CREATE INDEX IF NOT EXISTS "idx_messages_user_id" ON "messages" ("user_id");

-- Add foreign key constraints
ALTER TABLE "messages" ADD CONSTRAINT "messages_conversation_id_fkey" 
  FOREIGN KEY ("conversation_id") REFERENCES "conversations"("id") ON DELETE CASCADE ON UPDATE NO ACTION;

ALTER TABLE "messages" ADD CONSTRAINT "messages_animation_id_fkey" 
  FOREIGN KEY ("animation_id") REFERENCES "animations"("id") ON DELETE SET NULL ON UPDATE NO ACTION; 