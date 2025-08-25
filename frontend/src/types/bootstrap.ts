// types/bootstrap.ts
export type BotBrief = {
  id: number;
  username?: string | null;
  name?: string | null;
  telegram_id?: number | null;
  is_active: boolean;
  bot_url?: string | null;
};

export type GroupBrief = {
  id: number;
  telegram_id: number;
  name: string;
  type: string;
  is_active: boolean;
  photo?: string | null;
};

export type CommunityBrief = {
  id: number;
  table_key: string;
  domain: string;
};

export type CommunityAggregate = {
  community: CommunityBrief;
  role?: "owner" | "admin" | "moderator" | null;
  bot?: BotBrief | null;
  main_group?: GroupBrief | null;
  additional_group?: GroupBrief | null;
};

export type TelegramUserSchema = {
  id: number;
  first_name: string;
  last_name?: string | null;
  username?: string | null;
  language_code?: string | null;
  is_premium?: boolean;
  photo_url?: string | null;
};

export type BootstrapResponse = {
  user: TelegramUserSchema;
  communities: CommunityAggregate[];
};
