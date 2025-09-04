import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';
import { Shield, AlertTriangle, AlertCircle, CheckCircle } from 'lucide-react';

type CredibilityBadgeProps = {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  showScore?: boolean;
  className?: string;
};

const CredibilityBadge = ({
  score,
  size = 'md',
  showLabel = true,
  showScore = true,
  className,
}: CredibilityBadgeProps) => {
  // Get badge properties based on score
  const getBadgeProps = () => {
    if (score >= 80) {
      return {
        color: 'green',
        label: 'Likely Accurate',
        bg: 'bg-green-100',
        border: 'border-green-200',
        text: 'text-green-800',
        icon: <CheckCircle className="mr-2" />,
      };
    } else if (score >= 40) {
      return {
        color: 'yellow',
        label: 'Needs Context',
        bg: 'bg-yellow-100',
        border: 'border-yellow-200',
        text: 'text-yellow-800',
        icon: <AlertCircle className="mr-2" />,
      };
    } else {
      return {
        color: 'red',
        label: 'Likely Misleading',
        bg: 'bg-red-100',
        border: 'border-red-200',
        text: 'text-red-800',
        icon: <AlertTriangle className="mr-2" />,
      };
    }
  };

  const { color, label, bg, text, border, icon } = getBadgeProps();

  // Size variants
  const sizeClasses = {
    sm: 'text-xs px-2 py-1 rounded-md',
    md: 'text-sm px-3 py-1 rounded-lg',
    lg: 'text-base px-4 py-2 rounded-lg',
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  };

  const badgeClasses = cn(
    'font-medium border inline-flex items-center',
    bg,
    text,
    border,
    sizeClasses[size],
    className
  );

  // SVG arc path for circular score indicator
  const radius = size === 'lg' ? 15 : size === 'md' ? 12 : 10;
  const circumference = 2 * Math.PI * radius;
  const scoreOffset = circumference - (score / 100) * circumference;

  return (
    <div className={badgeClasses}>
      {showScore && (
        <div className={`relative ${size === 'sm' ? 'mr-2' : 'mr-3'}`}>
          <svg
            className={`transform -rotate-90 ${iconSizes[size]}`}
            viewBox="0 0 36 36"
          >
            <circle
              className="text-gray-200"
              strokeWidth="3"
              stroke="currentColor"
              fill="transparent"
              r={radius}
              cx="18"
              cy="18"
            />
            <motion.circle
              className={color === 'green' ? 'text-green-500' : color === 'yellow' ? 'text-yellow-500' : 'text-red-500'}
              strokeWidth="3"
              strokeLinecap="round"
              stroke="currentColor"
              fill="transparent"
              r={radius}
              cx="18"
              cy="18"
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset: scoreOffset }}
              transition={{ duration: 1, ease: "easeOut" }}
              strokeDasharray={circumference}
            />
            <text
              x="18"
              y="19"
              textAnchor="middle"
              dominantBaseline="middle"
              className={color === 'green' ? 'fill-green-700' : color === 'yellow' ? 'fill-yellow-700' : 'fill-red-700'}
              fontSize={size === 'lg' ? '9px' : size === 'md' ? '7px' : '6px'}
              fontWeight="bold"
            >
              {score}
            </text>
          </svg>
        </div>
      )}
      {React.cloneElement(icon, { className: iconSizes[size] })}
      {showLabel && <span>{label}</span>}
    </div>
  );
};

export default CredibilityBadge;
