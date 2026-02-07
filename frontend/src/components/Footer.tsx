// footer
import React from "react"
import { Box, Typography } from "@mui/material"
import { mainFontColor } from "../utils/constants"
import sockImg from "../assets/chaussette.png"

function Footer() {
    const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

    const handleDoubleClick = async () => {
        for (let i = 0; i < 30; i++) {
            const sock = document.createElement("img")
            sock.src = sockImg
            sock.className = "sock"
            sock.style.left = Math.random() * window.innerWidth + "px"
            const duration = 1 + Math.random() * 10
            sock.style.animationDuration = `${duration}s`
            sock.style.transform = `rotate(${Math.random() * 360}deg)`
            document.body.appendChild(sock)
            sock.addEventListener("animationend", () => {
                sock.remove()
            })
            await sleep(200)
        }
    }

    return (
        <Box
            sx={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                height: "30px",
                position: "relative",
                marginTop: "auto",
                width: "100%",
                backgroundColor: "transparent",
            }}
        >
            <Typography variant="body1" color={mainFontColor}>
                © 2026 <span onDoubleClick={handleDoubleClick}>Aurianne Schwartz</span> &{" "}
                <span>Léopold Chappuis</span>
                {process.env.REACT_APP_RELEASE_TAG && (
                    <span
                        style={{
                            fontSize: "0.8rem",
                            marginLeft: "10px",
                            opacity: 0.7,
                        }}
                    >
                        ({process.env.REACT_APP_RELEASE_TAG})
                    </span>
                )}
            </Typography>
        </Box>
    )
}
export default Footer
