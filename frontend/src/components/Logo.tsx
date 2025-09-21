import React from 'react';

const Logo: React.FC = () => {
  return (
    <svg width="64" height="64" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="bullBody" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{stopColor:'#FF4444', stopOpacity:1}} />
          <stop offset="50%" style={{stopColor:'#CC0000', stopOpacity:1}} />
          <stop offset="100%" style={{stopColor:'#990000', stopOpacity:1}} />
        </linearGradient>
        <linearGradient id="bullHorns" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{stopColor:'#FFDDDD', stopOpacity:1}} />
          <stop offset="100%" style={{stopColor:'#CC0000', stopOpacity:1}} />
        </linearGradient>
      </defs>
      
      {/* Background circle with subtle red */}
      <circle cx="16" cy="16" r="15" fill="#220000" stroke="#440000" strokeWidth="1"/>
      
      {/* Bull head - more defined shape */}
      <ellipse cx="16" cy="18" rx="8" ry="6" fill="url(#bullBody)"/>
      
      {/* Bull snout */}
      <ellipse cx="16" cy="22" rx="3" ry="2" fill="#AA0000"/>
      
      {/* Bull horns - more prominent and recognizable */}
      <path d="M10 12 L8 6 L12 10 Z" fill="url(#bullHorns)"/>
      <path d="M22 12 L24 6 L20 10 Z" fill="url(#bullHorns)"/>
      
      {/* Horn details */}
      <path d="M10 12 L9 8 L11 10 Z" fill="#FFAAAA"/>
      <path d="M22 12 L23 8 L21 10 Z" fill="#FFAAAA"/>
      
      {/* Bull eyes - larger and more visible */}
      <circle cx="13" cy="16" r="1.8" fill="white"/>
      <circle cx="19" cy="16" r="1.8" fill="white"/>
      <circle cx="13" cy="16" r="1" fill="black"/>
      <circle cx="19" cy="16" r="1" fill="black"/>
      
      {/* Eye highlights */}
      <circle cx="13.3" cy="15.5" r="0.4" fill="white"/>
      <circle cx="19.3" cy="15.5" r="0.4" fill="white"/>
      
      {/* Bull nostrils */}
      <ellipse cx="14.5" cy="20" rx="0.6" ry="0.4" fill="black"/>
      <ellipse cx="17.5" cy="20" rx="0.6" ry="0.4" fill="black"/>
      
      {/* Bull mouth */}
      <path d="M14 23 Q16 24 18 23" stroke="black" strokeWidth="0.8" fill="none"/>
      
      {/* Muscular definition - subtle */}
      <path d="M11 17 Q13 15 15 17" stroke="#660000" strokeWidth="0.5" fill="none" opacity="0.7"/>
      <path d="M17 17 Q19 15 21 17" stroke="#660000" strokeWidth="0.5" fill="none" opacity="0.7"/>
      
      {/* Highlight on head for 3D effect */}
      <ellipse cx="16" cy="14" rx="5" ry="2" fill="white" opacity="0.2"/>
    </svg>
  );
};

export default Logo;
