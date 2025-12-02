export default function NotFound() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-background text-foreground">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">404 - Page Not Found</h1>
        <p className="text-muted-foreground mb-4">
          The page you are looking for does not exist.
        </p>
        <a
          href="/"
          className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
        >
          Go Home
        </a>
      </div>
    </div>
  );
}