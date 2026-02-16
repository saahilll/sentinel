export interface App {
    id: string;
    name: string;
    slug: string;
    icon_url: string;
    description: string;
    framework: "fastapi" | "flask" | "django" | "starlette";
    created_at: string;
    updated_at: string;
}

export interface AppListItem {
    id: string;
    name: string;
    slug: string;
    icon_url: string;
    description: string;
    framework: "fastapi" | "flask" | "django" | "starlette";
    api_key_count: number;
    created_at: string;
}
