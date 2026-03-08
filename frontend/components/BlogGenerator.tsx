"use client"

import { useState } from "react"
import axios from "axios"
import ReactMarkdown from "react-markdown"

export default function BlogGenerator() {

    const [topic, setTopic] = useState("")
    const [blog, setBlog] = useState("")
    const [loading, setLoading] = useState(false)

    const generateBlog = async () => {

        if (!topic) {
            alert("Please enter a topic")
            return
        }

        setLoading(true)

        try {

            const response = await axios.post(
                "http://127.0.0.1:8000/generate",
                { topic }
            )

            setBlog(response.data.blog)

        } catch (error) {

            console.error(error)
            alert("Failed to generate blog")

        }

        setLoading(false)
    }

    return (

        <div className="min-h-screen flex flex-col items-center p-10">

            <h1 className="text-4xl font-bold mb-8">
                AI Blog Generator
            </h1>

            <div className="w-full max-w-2xl">

                <input
                    type="text"
                    placeholder="Enter blog topic..."
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    className="w-full border p-3 rounded mb-4"
                />

                <button
                    onClick={generateBlog}
                    className="bg-black text-white px-6 py-3 rounded"
                >
                    {loading ? "Generating..." : "Generate Blog"}
                </button>

            </div>

            {blog && (
                <div className="mt-12 w-full max-w-4xl bg-white text-black rounded-xl shadow-lg p-10">
                    <article className="prose lg:prose-lg max-w-none">
                        <ReactMarkdown>{blog}</ReactMarkdown>
                    </article>
                </div>
            )}


        </div>
    )
}