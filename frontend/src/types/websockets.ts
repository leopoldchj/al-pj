export enum WebSocketMessageType {
    // Message events
    MessageViewed = "MESSAGE_VIEWED",
    MessageCreated = "MESSAGE_CREATED",
    MessageDeleted = "MESSAGE_DELETED",

    // User presence events
    UserPresenceConnected = "USER_PRESENCE_CONNECTED",
    UserPresenceDisconnected = "USER_PRESENCE_DISCONNECTED",

    // BucketPoint (bucketlist) events
    BucketPointCreated = "BUCKETPOINT_CREATED",
    BucketPointDeleted = "BUCKETPOINT_DELETED",
    BucketPointUpdated = "BUCKETPOINT_UPDATED",

    // Photo events
    PhotoUploaded = "PHOTO_UPLOADED",
    PhotoDeleted = "PHOTO_DELETED",
    PhotoUpdated = "PHOTO_UPDATED",
    PhotoMoved = "PHOTO_MOVED",
    PhotoCopied = "PHOTO_COPIED",

    // Album events
    AlbumCreated = "ALBUM_CREATED",
    AlbumDeleted = "ALBUM_DELETED",
    AlbumUpdated = "ALBUM_UPDATED",

    // System events
    SystemNotification = "SYSTEM_NOTIFICATION",
}
