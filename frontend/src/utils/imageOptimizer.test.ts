import { optimizeImage } from "./imageOptimizer"
import imageCompression from "browser-image-compression"

jest.mock("browser-image-compression", () => jest.fn())

const mockImageCompression = imageCompression as jest.MockedFunction<typeof imageCompression>

function createFakeFile(name: string, type: string): File {
    return new File(["fake-image-data"], name, { type })
}

describe("optimizeImage", () => {
    beforeEach(() => {
        jest.clearAllMocks()
    })

    it("converts a .jpg file to .webp", async () => {
        const inputFile = createFakeFile("photo.jpg", "image/jpeg")
        const fakeBlob = new Blob(["compressed"], { type: "image/webp" })
        mockImageCompression.mockResolvedValue(fakeBlob as File)

        const result = await optimizeImage(inputFile)

        expect(result.name).toBe("photo.webp")
        expect(result.type).toBe("image/webp")
    })

    it("converts a .HEIC file to .webp with correct naming", async () => {
        const inputFile = createFakeFile("vacances.HEIC", "image/heic")
        const fakeBlob = new Blob(["compressed"], { type: "image/webp" })
        mockImageCompression.mockResolvedValue(fakeBlob as File)

        const result = await optimizeImage(inputFile)

        expect(result.name).toBe("vacances.webp")
        expect(result.type).toBe("image/webp")
    })

    it("passes the correct compression options", async () => {
        const inputFile = createFakeFile("test.png", "image/png")
        const fakeBlob = new Blob(["compressed"], { type: "image/webp" })
        mockImageCompression.mockResolvedValue(fakeBlob as File)

        await optimizeImage(inputFile)

        expect(mockImageCompression).toHaveBeenCalledWith(inputFile, {
            maxSizeMB: 1,
            maxWidthOrHeight: 1920,
            initialQuality: 0.8,
            fileType: "image/webp",
            preserveExif: false,
        })
    })

    it("handles a file without extension", async () => {
        const inputFile = createFakeFile("screenshot", "image/png")
        const fakeBlob = new Blob(["compressed"], { type: "image/webp" })
        mockImageCompression.mockResolvedValue(fakeBlob as File)

        const result = await optimizeImage(inputFile)

        expect(result.name).toBe("screenshot.webp")
    })

    it("propagates errors from the compression library", async () => {
        const inputFile = createFakeFile("corrupted.jpg", "image/jpeg")
        mockImageCompression.mockRejectedValue(new Error("Fichier corrompu"))

        await expect(optimizeImage(inputFile)).rejects.toThrow("Fichier corrompu")
    })
})
