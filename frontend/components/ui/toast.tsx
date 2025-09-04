import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react';
import { cn } from '../../lib/utils';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface ToastProps {
  message: string;
  type?: ToastType;
  duration?: number;
  onClose?: () => void;
  visible?: boolean;
}

const toastVariants = {
  initial: { opacity: 0, y: -20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};

const toastStyles = {
  success: 'bg-green-50 border-green-500 text-green-700',
  error: 'bg-red-50 border-red-500 text-red-700',
  info: 'bg-blue-50 border-blue-500 text-blue-700',
  warning: 'bg-yellow-50 border-yellow-500 text-yellow-700',
};

const toastIcons = {
  success: <CheckCircle className="h-5 w-5 text-green-500" />,
  error: <AlertCircle className="h-5 w-5 text-red-500" />,
  info: <Info className="h-5 w-5 text-blue-500" />,
  warning: <AlertCircle className="h-5 w-5 text-yellow-500" />,
};

export function Toast({
  message,
  type = 'info',
  duration = 3000,
  onClose,
  visible = true,
}: ToastProps) {
  const [isVisible, setIsVisible] = useState(visible);

  useEffect(() => {
    setIsVisible(visible);
    
    if (visible && duration !== Infinity) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        if (onClose) onClose();
      }, duration);
      
      return () => clearTimeout(timer);
    }
  }, [visible, duration, onClose]);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className="fixed top-4 right-4 z-50 max-w-md"
          initial="initial"
          animate="animate"
          exit="exit"
          variants={toastVariants}
          transition={{ duration: 0.2 }}
        >
          <div className={cn(
            'flex items-center p-4 shadow-lg rounded-lg border-l-4',
            toastStyles[type]
          )}>
            <div className="flex-shrink-0 mr-3">
              {toastIcons[type]}
            </div>
            <div className="flex-1 pr-3">
              <p className="text-sm font-medium">{message}</p>
            </div>
            <button
              onClick={() => {
                setIsVisible(false);
                if (onClose) onClose();
              }}
              className="flex-shrink-0 text-gray-400 hover:text-gray-500 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export function useToast() {
  const [toast, setToast] = useState<{
    message: string;
    type: ToastType;
    visible: boolean;
    id: number;
  }>({
    message: '',
    type: 'info',
    visible: false,
    id: 0
  });

  const showToast = (message: string, type: ToastType = 'info') => {
    setToast({
      message,
      type,
      visible: true,
      id: Date.now() // Generate a unique ID for each toast
    });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, visible: false }));
  };

  return {
    toast,
    showToast,
    hideToast
  };
}
