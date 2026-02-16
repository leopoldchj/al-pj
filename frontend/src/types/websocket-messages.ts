import { WebSocketMessageType } from "./websockets.js"
import {
    MessageViewed,
    MessageCreated,
    MessageDeleted,
    Presence,
    BucketPointDeleted,
    BucketPointCreated,
    BucketPointUpdated,
    PhotoUploaded,
    PhotoDeleted,
    PhotoUpdated,
    PhotoMoved,
    PhotoCopied,
    AlbumCreated,
    AlbumDeleted,
    AlbumUpdated,
    SystemNotification,
} from "./websocket-interfaces.js"

export interface WebSocketMessageTable {
    // Message types
    [WebSocketMessageType.MessageViewed]: MessageViewed
    [WebSocketMessageType.MessageCreated]: MessageCreated
    [WebSocketMessageType.MessageDeleted]: MessageDeleted

    // Presence types
    [WebSocketMessageType.UserPresenceConnected]: Presence
    [WebSocketMessageType.UserPresenceDisconnected]: Presence

    // BucketPoint types
    [WebSocketMessageType.BucketPointCreated]: BucketPointCreated
    [WebSocketMessageType.BucketPointDeleted]: BucketPointDeleted
    [WebSocketMessageType.BucketPointUpdated]: BucketPointUpdated

    // Photo types
    [WebSocketMessageType.PhotoUploaded]: PhotoUploaded
    [WebSocketMessageType.PhotoDeleted]: PhotoDeleted
    [WebSocketMessageType.PhotoUpdated]: PhotoUpdated
    [WebSocketMessageType.PhotoMoved]: PhotoMoved
    [WebSocketMessageType.PhotoCopied]: PhotoCopied

    // Album types
    [WebSocketMessageType.AlbumCreated]: AlbumCreated
    [WebSocketMessageType.AlbumDeleted]: AlbumDeleted
    [WebSocketMessageType.AlbumUpdated]: AlbumUpdated

    // System types
    [WebSocketMessageType.SystemNotification]: SystemNotification
}

export interface WebSocketMessage<T extends WebSocketMessageType> {
    type: T
    data: WebSocketMessageTable[T]
}
