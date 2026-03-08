import BlogGenerator from "@/components/BlogGenerator"

export default function Home() {
  return (
    <main className="min-h-screen bg-neutral-950 text-white flex flex-col items-center p-12">

      <div className="max-w-3xl text-center mb-10">
        <h1 className="text-4xl font-bold mb-3">
          AI Blog Generator
        </h1>

        <p className="text-neutral-400">
          Generate structured blog posts using a multi-agent AI pipeline
        </p>
      </div>

      <BlogGenerator />

    </main>
  )
}