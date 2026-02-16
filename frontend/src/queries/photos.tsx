import { useMutation, UseMutationResult, useQuery, UseQueryResult } from "@tanstack/react-query"
import { useAuth } from "../hooks/useAuth"
import { Photo } from "../types/photo"
import { useQueryClient } from "@tanstack/react-query"
import { AddPhotoInput } from "../types/photo"

export function useGetPhotos(
    albumId: string
): UseQueryResult<{ photos: Photo[]; album_id: string }, unknown> {
    const { axiosInstance } = useAuth()

    return useQuery<{ photos: Photo[]; album_id: string }, unknown>({
        queryKey: ["photos", albumId],
        queryFn: async () => {
            const response = await axiosInstance.get(`/photos/${albumId}/`)
            return response.data
        },
        enabled: !!albumId,
    })
}

export const useAddPhotoMutation = (): UseMutationResult<Photo, unknown, AddPhotoInput> => {
    const { axiosInstance } = useAuth()
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async ({ albumId, image, caption, location }: AddPhotoInput) => {
            const formData = new FormData()

            if (image) {
                formData.append("image", image)
            }
            if (caption) {
                formData.append("caption", caption)
            }
            if (location) {
                formData.append("location", location)
            }

            const response = await axiosInstance.post(`/photos/${albumId}/`, formData)

            return response.data
        },

        onSuccess: (_data, { albumId }) => {
            queryClient.invalidateQueries({ queryKey: ["photos", albumId] })
        },
    })
}

interface DeletePhotoInput {
    albumId: string
    photoId: number
}

export const useDeletePhotoMutation = (): UseMutationResult<void, unknown, DeletePhotoInput> => {
    const { axiosInstance } = useAuth()
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async ({ albumId, photoId }: DeletePhotoInput) => {
            await axiosInstance.delete(`/photos/${albumId}/${photoId}/`)
        },
        onSuccess: (_data, { albumId }) => {
            queryClient.invalidateQueries({ queryKey: ["photos", albumId] })
        },
    })
}

interface MovePhotoInput {
    albumId: string
    photoId: number
    targetAlbumId: number
}

export const useMovePhotoMutation = (): UseMutationResult<Photo, unknown, MovePhotoInput> => {
    const { axiosInstance } = useAuth()
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async ({ albumId, photoId, targetAlbumId }: MovePhotoInput) => {
            const response = await axiosInstance.post(`/photos/${albumId}/${photoId}/move/`, {
                target_album_id: targetAlbumId,
            })
            return response.data.photo
        },
        onSuccess: (_data, { albumId, targetAlbumId }) => {
            queryClient.invalidateQueries({ queryKey: ["photos", albumId] })
            queryClient.invalidateQueries({ queryKey: ["photos", String(targetAlbumId)] })
            queryClient.invalidateQueries({ queryKey: ["albums"] })
        },
    })
}

interface CopyPhotoInput {
    albumId: string
    photoId: number
    targetAlbumId: number
}

export const useCopyPhotoMutation = (): UseMutationResult<Photo, unknown, CopyPhotoInput> => {
    const { axiosInstance } = useAuth()
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async ({ albumId, photoId, targetAlbumId }: CopyPhotoInput) => {
            const response = await axiosInstance.post(`/photos/${albumId}/${photoId}/copy/`, {
                target_album_id: targetAlbumId,
            })
            return response.data.photo
        },
        onSuccess: (_data, { targetAlbumId }) => {
            queryClient.invalidateQueries({ queryKey: ["photos", String(targetAlbumId)] })
            queryClient.invalidateQueries({ queryKey: ["albums"] })
        },
    })
}

interface UpdatePhotoInput {
    albumId: string
    photoId: number
    data: Partial<Pick<Photo, "caption" | "location">> & { target_album_id?: number }
}

export const useUpdatePhotoMutation = (): UseMutationResult<Photo, unknown, UpdatePhotoInput> => {
    const { axiosInstance } = useAuth()
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async ({ albumId, photoId, data }: UpdatePhotoInput) => {
            const response = await axiosInstance.patch(`/photos/${albumId}/${photoId}/`, data)
            return response.data.photo
        },
        onSuccess: (_data, { albumId, data }) => {
            queryClient.invalidateQueries({ queryKey: ["photos", albumId] })
            if (data.target_album_id) {
                queryClient.invalidateQueries({
                    queryKey: ["photos", String(data.target_album_id)],
                })
            }
            queryClient.invalidateQueries({ queryKey: ["albums"] })
        },
    })
}
