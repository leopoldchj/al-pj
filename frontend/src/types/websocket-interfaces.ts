import IMessage from "./messages"
import IBucketPoint from "./bucketspoints"
import { Photo } from "./photo"

// Message interfaces
export interface MessageViewed {
    msgId: string
    userId: string
    timeCode: Date
}

export interface MessageCreated {
    message: IMessage
    sender: {
        id: number
        email: string
        username: string
    }
}

export interface MessageDeleted {
    message: IMessage
    sender: {
        id: number
        email: string
        username: string
    }
}

// Presence interface
export interface Presence {
    user_id: number
    name: string
}

// BucketPoint interfaces
export interface BucketPointDeleted {
    id: number
}

export interface BucketPointCreated {
    data: IBucketPoint
}

export interface BucketPointUpdated {
    data: IBucketPoint
}

// Photo interfaces
export interface PhotoUploaded {
    data: Photo
    album_id: number
}

export interface PhotoDeleted {
    id: number
    album_id: number
}

export interface PhotoUpdated {
    data: Photo
    album_id: number
}

export interface PhotoMoved {
    data: Photo
    source_album_id: number
    target_album_id: number
}

export interface PhotoCopied {
    data: Photo
    album_id: number
}

// Album interfaces
export interface Album {
    id: number
    title: string
    description: string | null
    created_at: string
    updated_at: string
    cover_image: string | null
}

export interface AlbumCreated {
    data: Album
}

export interface AlbumDeleted {
    id: number
}

export interface AlbumUpdated {
    data: Album
}

// System notification interface
export interface SystemNotification {
    message: string
    level: "info" | "warning" | "error"
    timestamp: string
}
