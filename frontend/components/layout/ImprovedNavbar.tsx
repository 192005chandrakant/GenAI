import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { 
  Shield, Menu, X, ChevronDown, User, Settings, 
  LogOut, Bell, Search, Home, BarChart2, BookOpen, 
  Users, ChevronRight, Sun, Moon, Info 
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/components/auth/AuthProvider';
import { signOut } from '@/lib/auth';
import { cn } from '../../lib/utils';

const ImprovedNavbar = () => {
  const { user, loading } = useAuth();
  const [isMobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isProfileMenuOpen, setProfileMenuOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  
  const pathname = usePathname();
  const router = useRouter();

  // Initialize dark mode state from global theme
  useEffect(() => {
    const checkTheme = () => {
      if (typeof window !== 'undefined' && window.__theme) {
        setIsDarkMode(window.__theme.current === 'dark');
      } else {
        // Fallback to checking document class
        setIsDarkMode(document.documentElement.classList.contains('dark'));
      }
    };
    
    checkTheme();
    
    // Check theme every second to stay in sync
    const interval = setInterval(checkTheme, 1000);
    return () => clearInterval(interval);
  }, []);

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 10) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close the menu when route changes
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  // Toggle functions
  const toggleMenu = () => setMobileMenuOpen(!isMobileMenuOpen);
  const toggleUserMenu = () => {
    setProfileMenuOpen(!isProfileMenuOpen);
    setIsNotificationsOpen(false);
  };
  const toggleNotifications = () => {
    setIsNotificationsOpen(!isNotificationsOpen);
    setProfileMenuOpen(false);
  };
  
  // Updated toggleDarkMode to use global theme system
  const toggleDarkMode = () => {
    if (typeof window !== 'undefined' && window.__theme) {
      window.__theme.toggle();
      setIsDarkMode(window.__theme.current === 'dark');
    }
  };
  
  const closeAllMenus = () => {
    setMobileMenuOpen(false);
    setProfileMenuOpen(false);
    setIsNotificationsOpen(false);
  };

  const isActive = (path: string) => {
    if (path === '/') {
      return pathname === '/';
    }
    return pathname?.startsWith(path);
  };

  const handleSignOut = async () => {
    await signOut();
    closeAllMenus();
    router.push('/');
  };

  // Navigation links with icons
  const navLinks = [
    { name: 'Home', path: '/', icon: <Home className="w-5 h-5" /> },
    { name: 'Analyze', path: '/analyze', icon: <Search className="w-5 h-5" /> },
    { name: 'Learn', path: '/learn', icon: <BookOpen className="w-5 h-5" /> },
    { name: 'Community', path: '/community', icon: <Users className="w-5 h-5" /> },
    { 
      name: 'Dashboard', 
      path: '/dashboard', 
      icon: <BarChart2 className="w-5 h-5" />, 
      authRequired: true 
    },
  ];

  // Sample notifications
  const notifications = [
    {
      id: 1,
      title: 'Analysis complete',
      message: 'Your content has been analyzed successfully.',
      time: '2 min ago',
      read: false
    },
    {
      id: 2,
      title: 'New badge earned',
      message: 'Congratulations! You earned the "Fact Checker" badge.',
      time: '1 hour ago',
      read: true
    },
    {
      id: 3,
      title: 'Learning module unlocked',
      message: 'A new learning module on visual misinformation is now available.',
      time: '1 day ago',
      read: true
    }
  ];

  return (
    <nav 
      className={cn(
        "sticky top-0 z-50 w-full transition-all duration-200",
        scrolled 
          ? "bg-white/90 dark:bg-gray-900/90 backdrop-blur-md shadow-sm" 
          : "bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm"
      )}
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2" onClick={closeAllMenus}>
              <Shield className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              <span className="text-xl font-semibold text-gray-900 dark:text-white">MisinfoGuard</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-1">
            {navLinks.map((link) => (
              !link.authRequired || user ? (
                <Link 
                  key={link.path} 
                  href={link.path}
                  className={cn(
                    "flex items-center px-3 py-2 rounded-md text-sm font-medium transition-all",
                    isActive(link.path) 
                      ? "text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30" 
                      : "text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-50 dark:hover:bg-gray-800/60"
                  )}
                >
                  <span className="mr-2">{link.icon}</span>
                  {link.name}
                </Link>
              ) : null
            ))}
          </div>

          {/* Desktop Right-side Icons */}
          <div className="hidden md:flex items-center space-x-2">
            {/* Theme toggle */}
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-full text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              aria-label="Toggle theme"
            >
              {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            
            {/* Notifications */}
            <div className="relative">
              <button
                onClick={toggleNotifications}
                className="p-2 rounded-full text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                aria-label="Notifications"
              >
                <Bell className="w-5 h-5" />
                {notifications.some(n => !n.read) && (
                  <span className="absolute top-1 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
                )}
              </button>
              
              <AnimatePresence>
                {isNotificationsOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    transition={{ duration: 0.2 }}
                    className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 z-50 border border-gray-200 dark:border-gray-700"
                  >
                    <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
                      <h3 className="font-semibold text-gray-900 dark:text-white">Notifications</h3>
                      <button className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                        Mark all as read
                      </button>
                    </div>
                    
                    <div className="max-h-60 overflow-y-auto">
                      {notifications.length ? (
                        notifications.map(notification => (
                          <div 
                            key={notification.id}
                            className={cn(
                              "px-4 py-3 border-b border-gray-100 dark:border-gray-700 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer",
                              notification.read ? "" : "bg-blue-50 dark:bg-blue-900/20"
                            )}
                          >
                            <div className="flex justify-between">
                              <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                                {notification.title}
                              </h4>
                              <span className="text-xs text-gray-500 dark:text-gray-400">{notification.time}</span>
                            </div>
                            <p className="text-xs text-gray-600 dark:text-gray-300 mt-1">{notification.message}</p>
                          </div>
                        ))
                      ) : (
                        <p className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400 text-center">
                          No notifications
                        </p>
                      )}
                    </div>
                    
                    <div className="px-4 py-2 border-t border-gray-100 dark:border-gray-700">
                      <Link 
                        href="/notifications" 
                        className="text-xs text-center block text-blue-600 dark:text-blue-400 hover:underline"
                        onClick={closeAllMenus}
                      >
                        View all notifications
                      </Link>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Auth Buttons / User Menu (Desktop) */}
            {!user ? (
              <div className="flex items-center space-x-2">
                <Link 
                  href="/auth/login" 
                  className="px-4 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  Log in
                </Link>
                <Link 
                  href="/auth/register" 
                  className="px-4 py-2 rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 transition-colors"
                >
                  Sign up
                </Link>
              </div>
            ) : (
              <div className="relative">
                <button
                  onClick={toggleUserMenu}
                  className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  aria-label="User menu"
                >
                  <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center overflow-hidden">
                    {user?.photoURL ? (
                      <img src={user.photoURL} alt={user.displayName || "User"} className="w-full h-full object-cover" />
                    ) : (
                      <User className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    )}
                  </div>
                  <div className="flex items-center">
                    <span>{user?.displayName?.split(' ')[0] || "User"}</span>
                    <ChevronDown className="w-4 h-4 ml-1 opacity-70" />
                  </div>
                </button>

                <AnimatePresence>
                  {isProfileMenuOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 10 }}
                      transition={{ duration: 0.2 }}
                      className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 z-50 border border-gray-200 dark:border-gray-700"
                    >
                      <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                        <div className="flex items-center">
                          <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center overflow-hidden mr-3">
                            {user?.photoURL ? (
                              <img src={user.photoURL} alt={user.displayName || "User"} className="w-full h-full object-cover" />
                            ) : (
                              <User className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                            )}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">{user?.displayName}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user?.email}</p>
                          </div>
                        </div>
                        
                        
                      </div>
                      
                      <div className="py-1">
                        <Link
                          href="/dashboard"
                          className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                          onClick={closeAllMenus}
                        >
                          <BarChart2 className="w-4 h-4 mr-3" />
                          Dashboard
                        </Link>
                        <Link
                          href="/dashboard/settings"
                          className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                          onClick={closeAllMenus}
                        >
                          <Settings className="w-4 h-4 mr-3" />
                          Account Settings
                        </Link>
                        
                      </div>
                      
                      <div className="border-t border-gray-100 dark:border-gray-700 py-1">
                        <button
                          onClick={handleSignOut}
                          className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-left"
                        >
                          <LogOut className="w-4 h-4 mr-3" />
                          Sign out
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center space-x-2">
            {user && (
              <button
                onClick={toggleNotifications}
                className="p-2 rounded-full text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                aria-label="Notifications"
              >
                <Bell className="w-5 h-5" />
                {notifications.some(n => !n.read) && (
                  <span className="absolute top-3 right-16 w-2 h-2 bg-red-500 rounded-full"></span>
                )}
              </button>
            )}
            
            <button
              className="p-2 rounded-md text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              onClick={toggleMenu}
              aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
            >
              {isMobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 shadow-lg"
          >
            <div className="max-h-[calc(100vh-4rem)] overflow-y-auto">
              {/* User profile section (when logged in) */}
              {user && (
                <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                  <div className="flex items-center">
                    <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center overflow-hidden mr-3">
                      {user?.photoURL ? (
                        <img src={user.photoURL} alt={user.displayName || "User"} className="w-full h-full object-cover" />
                      ) : (
                        <User className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{user?.displayName || "User"}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user?.email}</p>
                    </div>
                  </div>
                  
                  
                </div>
              )}
              
              {/* Navigation Links */}
              <div className="px-2 py-3 space-y-1">
                {navLinks.map((link) => (
                  !link.authRequired || user ? (
                    <Link
                      key={link.path}
                      href={link.path}
                      className={cn(
                        "flex items-center px-4 py-2 rounded-md text-base font-medium transition-colors",
                        isActive(link.path) 
                          ? "text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30" 
                          : "text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50"
                      )}
                      onClick={closeAllMenus}
                    >
                      <span className="mr-3">{link.icon}</span>
                      {link.name}
                      <ChevronRight className="w-4 h-4 ml-auto opacity-70" />
                    </Link>
                  ) : null
                ))}
                
                {/* About/Help Link */}
                <Link
                  href="/about"
                  className="flex items-center px-4 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  onClick={closeAllMenus}
                >
                  <Info className="w-5 h-5 mr-3" />
                  About
                  <ChevronRight className="w-4 h-4 ml-auto opacity-70" />
                </Link>
                
                {/* Theme Toggle */}
                <div className="px-4 py-2 flex justify-between items-center">
                  <div className="flex items-center">
                    <Sun className="w-5 h-5 mr-3 text-gray-700 dark:text-gray-200" />
                    <span className="text-gray-700 dark:text-gray-200 font-medium">Dark mode</span>
                  </div>
                  <button
                    onClick={toggleDarkMode}
                    className={cn(
                      "relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none",
                      isDarkMode ? "bg-blue-600" : "bg-gray-200 dark:bg-gray-700"
                    )}
                  >
                    <span
                      className={cn(
                        "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                        isDarkMode ? "translate-x-6" : "translate-x-1"
                      )}
                    />
                  </button>
                </div>
              </div>
              
              {/* Auth Section */}
              <div className="px-4 py-3 border-t border-gray-100 dark:border-gray-700">
                {!user ? (
                  <div className="grid grid-cols-2 gap-3">
                    <Link
                      href="/auth/login"
                      className="w-full px-4 py-2 text-center rounded-md text-sm font-medium text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                      onClick={closeAllMenus}
                    >
                      Log in
                    </Link>
                    <Link
                      href="/auth/register"
                      className="w-full px-4 py-2 text-center rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 transition-colors"
                      onClick={closeAllMenus}
                    >
                      Sign up
                    </Link>
                  </div>
                ) : (
                  <>
                    
                    <Link
                      href="/dashboard/settings"
                      className="block w-full px-4 py-2 text-left rounded-md text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors mb-2"
                      onClick={closeAllMenus}
                    >
                      <div className="flex items-center">
                        <Settings className="w-4 h-4 mr-3" />
                        Account Settings
                      </div>
                    </Link>
                    <button
                      onClick={handleSignOut}
                      className="block w-full px-4 py-2 text-left rounded-md text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                    >
                      <div className="flex items-center">
                        <LogOut className="w-4 h-4 mr-3" />
                        Sign out
                      </div>
                    </button>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Notifications Panel (Mobile) */}
      <AnimatePresence>
        {isNotificationsOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700 shadow-lg"
          >
            <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
              <h3 className="font-semibold text-gray-900 dark:text-white">Notifications</h3>
              <button className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                Mark all as read
              </button>
            </div>
            
            <div className="max-h-60 overflow-y-auto">
              {notifications.length ? (
                notifications.map(notification => (
                  <div 
                    key={notification.id}
                    className={cn(
                      "px-4 py-3 border-b border-gray-100 dark:border-gray-700 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer",
                      notification.read ? "" : "bg-blue-50 dark:bg-blue-900/20"
                    )}
                  >
                    <div className="flex justify-between">
                      <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                        {notification.title}
                      </h4>
                      <span className="text-xs text-gray-500 dark:text-gray-400">{notification.time}</span>
                    </div>
                    <p className="text-xs text-gray-600 dark:text-gray-300 mt-1">{notification.message}</p>
                  </div>
                ))
              ) : (
                <p className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400 text-center">
                  No notifications
                </p>
              )}
            </div>
            
            <div className="px-4 py-3 border-t border-gray-100 dark:border-gray-700">
              <Link 
                href="/notifications" 
                className="text-sm text-center block text-blue-600 dark:text-blue-400 hover:underline"
                onClick={closeAllMenus}
              >
                View all notifications
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default ImprovedNavbar;
