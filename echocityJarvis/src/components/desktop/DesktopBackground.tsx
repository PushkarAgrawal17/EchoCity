export function DesktopBackground() {
  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      <div
        className="absolute inset-0 opacity-[0.35]"
        style={{
          backgroundImage:
            'linear-gradient(rgba(148,255,200,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(148,255,200,0.05) 1px, transparent 1px)',
          backgroundSize: '48px 48px',
        }}
      />
      <svg className="absolute inset-0 h-full w-full opacity-[0.18]" xmlns="http://www.w3.org/2000/svg">
        <circle cx="88%" cy="18%" r="90" fill="none" stroke="#39ff9d" strokeWidth="1" />
        <circle cx="88%" cy="18%" r="3" fill="#39ff9d" />
        <line x1="88%" y1="18%" x2="70%" y2="40%" stroke="#39ff9d" strokeWidth="1" />
        <line x1="88%" y1="18%" x2="97%" y2="45%" stroke="#39ff9d" strokeWidth="1" />
        <circle cx="70%" cy="40%" r="3" fill="#39ff9d" />
        <circle cx="97%" cy="45%" r="3" fill="#39ff9d" />
        <circle cx="14%" cy="82%" r="70" fill="none" stroke="#5fe3ff" strokeWidth="1" />
        <line x1="14%" y1="82%" x2="30%" y2="65%" stroke="#5fe3ff" strokeWidth="1" />
        <circle cx="30%" cy="65%" r="2.5" fill="#5fe3ff" />
      </svg>
      {/* sparkle motif echoing the reference video's bottom-right marker */}
      <svg className="absolute bottom-6 right-6 h-8 w-8 opacity-70" viewBox="0 0 32 32" fill="none">
        <path d="M16 0 L19 13 L32 16 L19 19 L16 32 L13 19 L0 16 L13 13 Z" fill="#e8f6ee" opacity="0.8" />
      </svg>
    </div>
  );
}
