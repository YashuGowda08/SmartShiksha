import Dexie, { type Table } from "dexie";

export interface OfflineSubject {
  id: string | number;
  name: string;
  description?: string;
  icon?: string;
  color?: string;
  classes?: string[];
}

export interface OfflineChapter {
  id: string | number;
  subject_id?: string | number;
  name: string;
  description?: string;
  order_index?: number;
}

export interface OfflineTopic {
  id: string | number;
  chapter_id?: string | number;
  name: string;
  explanation?: string;
  examples?: string;
  order_index?: number;
}

class SmartShikshaDB extends Dexie {
  subjects!: Table<OfflineSubject>;
  chapters!: Table<OfflineChapter>;
  topics!: Table<OfflineTopic>;

  constructor() {
    super("SmartShikshaDB");
    this.version(1).stores({
      subjects: "++id",
      chapters: "++id",
      topics: "++id",
    });
  }
}

export const db = new SmartShikshaDB();
