import imageCompression from "browser-image-compression"

const COMPRESSION_OPTIONS: Parameters<typeof imageCompression>[1] = {
    maxSizeMB: 1,
    maxWidthOrHeight: 1920,
    initialQuality: 0.8,
    fileType: "image/webp",
    preserveExif: false,
}

function replaceExtensionWithWebp(filename: string): string {
    const dotIndex = filename.lastIndexOf(".")
    const baseName = dotIndex !== -1 ? filename.substring(0, dotIndex) : filename
    return `${baseName}.webp`
}

export async function optimizeImage(file: File): Promise<File> {
    const compressedBlob = await imageCompression(file, COMPRESSION_OPTIONS)

    const newFileName = replaceExtensionWithWebp(file.name)

    return new File([compressedBlob], newFileName, { type: "image/webp" })
}
