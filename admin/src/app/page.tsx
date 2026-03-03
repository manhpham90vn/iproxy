import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth"

export default function Home() {
  const router = useRouter()
  const token = useAuthStore((state) => state.token)

  useEffect(() => {
    if (token) {
      router.push("/dashboard")
    } else {
      router.push("/login")
    }
  }, [token, router])

  return null
}
