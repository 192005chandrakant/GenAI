'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Settings, User, LogOut, ChevronDown, Bell, Lock, Key, UserCheck, Eye, Moon, Sun, Globe, HelpCircle } from 'lucide-react';
import MainLayout from '../../../components/layout/MainLayout';
import { toast } from 'react-hot-toast';

import { useAuth } from '@/components/auth/AuthProvider';
import { signOut } from '@/lib/auth';

interface SettingsCategory {
  id: string;
  title: string;
  icon: React.ReactNode;
  description: string;
}

interface LanguageOption {
  code: string;
  name: string;
  localName: string;
}

export default function SettingsPage() {
  const { user, loading } = useAuth();
  const [activeCategory, setActiveCategory] = useState<string>('account');
  const [passwordValues, setPasswordValues] = useState({
    current: '',
    new: '',
    confirm: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    activitySummary: true,
    newFeatures: false,
    securityAlerts: true,
  });
  const [appearance, setAppearance] = useState<'light' | 'dark' | 'system'>('system');
  const [language, setLanguage] = useState<string>('en');
  
  const categories: SettingsCategory[] = [
    {
      id: 'account',
      title: 'Account',
      icon: <User className="w-5 h-5" />,
      description: 'Manage your account settings and preferences'
    },
    {
      id: 'security',
      title: 'Security',
      icon: <Lock className="w-5 h-5" />,
      description: 'Update password and security settings'
    },
    {
      id: 'notifications',
      title: 'Notifications',
      icon: <Bell className="w-5 h-5" />,
      description: 'Configure how you want to be notified'
    },
    {
      id: 'appearance',
      title: 'Appearance',
      icon: <Moon className="w-5 h-5" />,
      description: 'Customize your visual experience'
    },
    {
      id: 'language',
      title: 'Language',
      icon: <Globe className="w-5 h-5" />,
      description: 'Change your preferred language'
    },
    {
      id: 'help',
      title: 'Help & Support',
      icon: <HelpCircle className="w-5 h-5" />,
      description: 'Get help with using the platform'
    },
  ];
  
  const languageOptions: LanguageOption[] = [
    { code: 'en', name: 'English', localName: 'English' },
    { code: 'hi', name: 'Hindi', localName: 'हिन्दी' },
    { code: 'te', name: 'Telugu', localName: 'తెలుగు' },
    { code: 'ta', name: 'Tamil', localName: 'தமிழ்' },
    { code: 'mr', name: 'Marathi', localName: 'मराठी' },
    { code: 'bn', name: 'Bengali', localName: 'বাংলা' },
    { code: 'kn', name: 'Kannada', localName: 'ಕನ್ನಡ' },
    { code: 'ml', name: 'Malayalam', localName: 'മലയാളം' },
  ];
  
  const handlePasswordChange = () => {
    if (passwordValues.new !== passwordValues.confirm) {
      toast.error('New passwords do not match');
      return;
    }
    
    if (passwordValues.new.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }
    
    // Simulate API call
    setTimeout(() => {
      toast.success('Password updated successfully');
      setPasswordValues({
        current: '',
        new: '',
        confirm: '',
      });
    }, 1000);
  };
  
  const handleAppearanceChange = (value: 'light' | 'dark' | 'system') => {
    setAppearance(value);
    toast.success(`Appearance set to ${value} mode`);
    // In a real app, would persist this to local storage/cookies
  };
  
  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setLanguage(e.target.value);
    const selectedLanguage = languageOptions.find(option => option.code === e.target.value);
    toast.success(`Language changed to ${selectedLanguage?.name}`);
    // In a real app, would call an API to update user preferences
  };
  
  const handleSaveNotifications = () => {
    toast.success('Notification preferences updated');
    // In a real app, would call an API to update notification settings
  };
  
  const handleLogout = async () => {
    await signOut();
    toast.success('Logged out successfully');
    // Then redirect to login page
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row gap-8">
          {/* Sidebar */}
          <div className="md:w-64 shrink-0">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 sticky top-24">
              <h2 className="font-semibold text-gray-900 mb-4 flex items-center">
                <Settings className="w-5 h-5 mr-2" />
                Settings
              </h2>
              
              <nav className="space-y-1">
                {categories.map((category) => (
                  <button
                    key={category.id}
                    onClick={() => setActiveCategory(category.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg flex items-center transition ${
                      activeCategory === category.id
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <span className="mr-3">{category.icon}</span>
                    <span>{category.title}</span>
                  </button>
                ))}
                
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-3 py-2 rounded-lg flex items-center text-red-600 hover:bg-red-50 transition mt-4"
                >
                  <LogOut className="w-5 h-5 mr-3" />
                  <span>Log Out</span>
                </button>
              </nav>
            </div>
          </div>
          
          {/* Main Content Area */}
          <div className="flex-1">
            {/* Account Settings */}
            {activeCategory === 'account' && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
              >
                <h1 className="text-2xl font-semibold text-gray-900 mb-1">Account Settings</h1>
                <p className="text-gray-600 mb-6">{categories.find(c => c.id === 'account')?.description}</p>
                
                <div className="space-y-6">
                  {/* Profile Information */}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Profile Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Full Name
                        </label>
                        <input
                          type="text"
                          defaultValue={user?.displayName || ''}
                          className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Display Name
                        </label>
                        <input
                          type="text"
                          defaultValue={user?.displayName?.split(' ')[0] || ''}
                          className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Email Address
                        </label>
                        <input
                          type="email"
                          defaultValue={user?.email || ''}
                          disabled
                          className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-gray-100"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Phone Number
                        </label>
                        <input
                          type="tel"
                          defaultValue={user?.phoneNumber || ''}
                          className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                    </div>
                  </div>
                  
                  {/* Profile Picture */}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Profile Picture</h3>
                    <div className="flex items-center">
                      <div className="w-20 h-20 rounded-full bg-gray-200 flex items-center justify-center overflow-hidden mr-6">
                        {user?.photoURL ? (
                          <img src={user.photoURL} alt="Profile" className="w-full h-full object-cover" />
                        ) : (
                          <User className="w-10 h-10 text-gray-500" />
                        )}
                      </div>
                      <div className="space-x-3">
                        <button className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium hover:bg-gray-50 transition">
                          Upload New
                        </button>
                        <button className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-red-600 hover:bg-red-50 transition">
                          Remove
                        </button>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 mt-2">Recommended: Square image, at least 400x400 pixels</p>
                  </div>
                  
                  {/* Bio */}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Bio</h3>
                    <textarea
                      rows={4}
                      defaultValue="I'm passionate about fighting misinformation and helping others find reliable information."
                      className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    ></textarea>
                    <p className="text-xs text-gray-500 mt-1">Brief description of yourself (max 200 characters)</p>
                  </div>
                  
                  {/* Save Button */}
                  <div className="pt-4">
                    <button 
                      onClick={() => toast.success('Profile updated successfully')}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Save Changes
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
            
            {/* Security Settings */}
            {activeCategory === 'security' && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
              >
                <h1 className="text-2xl font-semibold text-gray-900 mb-1">Security Settings</h1>
                <p className="text-gray-600 mb-6">{categories.find(c => c.id === 'security')?.description}</p>
                
                <div className="space-y-8">
                  {/* Change Password */}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Change Password</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Current Password
                        </label>
                        <div className="relative">
                          <input
                            type={showPassword ? 'text' : 'password'}
                            value={passwordValues.current}
                            onChange={(e) => setPasswordValues({...passwordValues, current: e.target.value})}
                            className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 pr-10"
                          />
                          <button 
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                          >
                            <Eye className="h-5 w-5" />
                          </button>
                        </div>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          New Password
                        </label>
                        <input
                          type={showPassword ? 'text' : 'password'}
                          value={passwordValues.new}
                          onChange={(e) => setPasswordValues({...passwordValues, new: e.target.value})}
                          className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Confirm New Password
                        </label>
                        <input
                          type={showPassword ? 'text' : 'password'}
                          value={passwordValues.confirm}
                          onChange={(e) => setPasswordValues({...passwordValues, confirm: e.target.value})}
                          className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      
                      <div className="flex items-center mt-1">
                        <input
                          id="show-password"
                          name="show-password"
                          type="checkbox"
                          checked={showPassword}
                          onChange={() => setShowPassword(!showPassword)}
                          className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                        />
                        <label htmlFor="show-password" className="ml-2 block text-sm text-gray-600">
                          Show passwords
                        </label>
                      </div>
                      
                      <button
                        onClick={handlePasswordChange}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors mt-2"
                      >
                        Update Password
                      </button>
                    </div>
                  </div>
                  
                  {/* Two-Factor Authentication */}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Two-Factor Authentication</h3>
                    <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div>
                        <h4 className="font-medium text-gray-900">Protect your account with 2FA</h4>
                        <p className="text-sm text-gray-600">Add an extra layer of security to your account</p>
                      </div>
                      <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                        Enable
                      </button>
                    </div>
                  </div>
                  
                  {/* Login Sessions */}
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Active Sessions</h3>
                    <div className="border border-gray-200 rounded-lg divide-y divide-gray-200">
                      <div className="p-4 flex justify-between items-center">
                        <div>
                          <p className="font-medium text-gray-900">Current Session</p>
                          <p className="text-sm text-gray-600">Windows 11 • Chrome • Mumbai, India</p>
                          <p className="text-xs text-gray-500 mt-1">Started: 2 hours ago</p>
                        </div>
                        <div className="flex items-center text-sm text-green-600">
                          <UserCheck className="w-4 h-4 mr-1" />
                          <span>Active Now</span>
                        </div>
                      </div>
                      
                      <div className="p-4 flex justify-between items-center">
                        <div>
                          <p className="font-medium text-gray-900">Mobile App</p>
                          <p className="text-sm text-gray-600">Android 13 • Mumbai, India</p>
                          <p className="text-xs text-gray-500 mt-1">Last active: 3 days ago</p>
                        </div>
                        <button className="text-sm text-red-600 hover:text-red-800">
                          Sign Out
                        </button>
                      </div>
                    </div>
                    
                    <button className="mt-4 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium hover:bg-gray-50 transition">
                      Sign out of all sessions
                    </button>
                  </div>
                  
                  {/* Delete Account */}
                  <div className="pt-4 border-t border-gray-200">
                    <h3 className="text-lg font-medium text-red-600 mb-2">Danger Zone</h3>
                    <p className="text-sm text-gray-600 mb-4">Once you delete your account, there is no going back. Please be certain.</p>
                    <button 
                      onClick={() => toast.error('This action is disabled in the demo')}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      Delete Account
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
            
            {/* Notifications Settings */}
            {activeCategory === 'notifications' && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
              >
                <h1 className="text-2xl font-semibold text-gray-900 mb-1">Notification Settings</h1>
                <p className="text-gray-600 mb-6">{categories.find(c => c.id === 'notifications')?.description}</p>
                
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Email Notifications</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">Email Alerts</h4>
                          <p className="text-sm text-gray-600">Receive emails about your account activity</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input 
                            type="checkbox" 
                            checked={notifications.emailAlerts}
                            onChange={() => setNotifications({...notifications, emailAlerts: !notifications.emailAlerts})}
                            className="sr-only peer" 
                          />
                          <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-4 peer-focus:ring-blue-300 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">Weekly Activity Summary</h4>
                          <p className="text-sm text-gray-600">Weekly report of your fact-checking activity</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input 
                            type="checkbox" 
                            checked={notifications.activitySummary}
                            onChange={() => setNotifications({...notifications, activitySummary: !notifications.activitySummary})}
                            className="sr-only peer" 
                          />
                          <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-4 peer-focus:ring-blue-300 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">New Features & Updates</h4>
                          <p className="text-sm text-gray-600">Stay informed about new features and improvements</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input 
                            type="checkbox" 
                            checked={notifications.newFeatures}
                            onChange={() => setNotifications({...notifications, newFeatures: !notifications.newFeatures})}
                            className="sr-only peer" 
                          />
                          <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-4 peer-focus:ring-blue-300 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">Security Alerts</h4>
                          <p className="text-sm text-gray-600">Important security-related notifications</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input 
                            type="checkbox" 
                            checked={notifications.securityAlerts}
                            onChange={() => setNotifications({...notifications, securityAlerts: !notifications.securityAlerts})}
                            className="sr-only peer" 
                          />
                          <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-4 peer-focus:ring-blue-300 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Push Notifications</h3>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-center text-gray-600">Download our mobile app to enable push notifications</p>
                      <div className="flex justify-center mt-3 space-x-4">
                        <button className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors flex items-center">
                          <span>iOS App</span>
                        </button>
                        <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center">
                          <span>Android App</span>
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  <div className="pt-4">
                    <button 
                      onClick={handleSaveNotifications}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Save Preferences
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
            
            {/* Appearance Settings */}
            {activeCategory === 'appearance' && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
              >
                <h1 className="text-2xl font-semibold text-gray-900 mb-1">Appearance Settings</h1>
                <p className="text-gray-600 mb-6">{categories.find(c => c.id === 'appearance')?.description}</p>
                
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Theme</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div
                      onClick={() => handleAppearanceChange('light')}
                      className={`cursor-pointer border rounded-lg p-4 flex flex-col items-center transition ${
                        appearance === 'light' ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200' : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center border border-gray-200 mb-3">
                        <Sun className="w-6 h-6 text-yellow-500" />
                      </div>
                      <h4 className="font-medium text-gray-900">Light</h4>
                      <p className="text-xs text-gray-500 text-center mt-1">Light mode interface</p>
                    </div>
                    
                    <div
                      onClick={() => handleAppearanceChange('dark')}
                      className={`cursor-pointer border rounded-lg p-4 flex flex-col items-center transition ${
                        appearance === 'dark' ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200' : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="w-12 h-12 rounded-full bg-gray-900 flex items-center justify-center mb-3">
                        <Moon className="w-6 h-6 text-white" />
                      </div>
                      <h4 className="font-medium text-gray-900">Dark</h4>
                      <p className="text-xs text-gray-500 text-center mt-1">Dark mode interface</p>
                    </div>
                    
                    <div
                      onClick={() => handleAppearanceChange('system')}
                      className={`cursor-pointer border rounded-lg p-4 flex flex-col items-center transition ${
                        appearance === 'system' ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200' : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="w-12 h-12 rounded-full bg-gradient-to-r from-gray-900 to-white flex items-center justify-center mb-3">
                        <Settings className="w-6 h-6 text-gray-700" />
                      </div>
                      <h4 className="font-medium text-gray-900">System</h4>
                      <p className="text-xs text-gray-500 text-center mt-1">Follow system settings</p>
                    </div>
                  </div>
                </div>
                
                <div className="mt-8">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Text Size</h3>
                  <div>
                    <input
                      type="range"
                      min="1"
                      max="5"
                      step="1"
                      defaultValue="3"
                      className="w-full"
                    />
                    <div className="flex justify-between mt-1 text-sm text-gray-500">
                      <span>Small</span>
                      <span>Default</span>
                      <span>Large</span>
                    </div>
                  </div>
                </div>
                
                <div className="mt-8">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Color Blindness Support</h3>
                  <div className="flex items-center">
                    <input
                      id="color-blindness"
                      name="color-blindness"
                      type="checkbox"
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                    />
                    <label htmlFor="color-blindness" className="ml-2 block text-gray-600">
                      Enable color blindness friendly mode
                    </label>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Optimizes color contrasts and indicator styles for better visibility</p>
                </div>
              </motion.div>
            )}
            
            {/* Language Settings */}
            {activeCategory === 'language' && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
              >
                <h1 className="text-2xl font-semibold text-gray-900 mb-1">Language Settings</h1>
                <p className="text-gray-600 mb-6">{categories.find(c => c.id === 'language')?.description}</p>
                
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Interface Language</h3>
                  <select
                    value={language}
                    onChange={handleLanguageChange}
                    className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    {languageOptions.map((option) => (
                      <option key={option.code} value={option.code}>
                        {option.name} ({option.localName})
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500 mt-2">This will change the language of the user interface</p>
                </div>
                
                <div className="mt-8">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Fact-Checking Languages</h3>
                  <p className="text-gray-600 mb-3">Select languages for content you can check</p>
                  
                  <div className="space-y-3">
                    {languageOptions.map((option) => (
                      <div key={option.code} className="flex items-center">
                        <input
                          id={`lang-${option.code}`}
                          name={`lang-${option.code}`}
                          type="checkbox"
                          defaultChecked={option.code === 'en' || option.code === 'hi'}
                          className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                        />
                        <label htmlFor={`lang-${option.code}`} className="ml-2 block text-gray-600">
                          {option.name} ({option.localName})
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="pt-6 mt-6 border-t border-gray-200">
                  <button 
                    onClick={() => toast.success('Language settings updated')}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Save Language Settings
                  </button>
                </div>
              </motion.div>
            )}
            
            {/* Help & Support */}
            {activeCategory === 'help' && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
              >
                <h1 className="text-2xl font-semibold text-gray-900 mb-1">Help & Support</h1>
                <p className="text-gray-600 mb-6">{categories.find(c => c.id === 'help')?.description}</p>
                
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Frequently Asked Questions</h3>
                    <div className="space-y-3">
                      <div className="border border-gray-200 rounded-lg">
                        <button
                          className="flex justify-between items-center w-full p-4 text-left"
                          onClick={(e) => {
                            e.currentTarget.setAttribute('aria-expanded', 
                              e.currentTarget.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'
                            );
                            e.currentTarget.nextElementSibling?.classList.toggle('hidden');
                          }}
                          aria-expanded="false"
                        >
                          <span className="font-medium text-gray-900">How does the fact-checking process work?</span>
                          <ChevronDown className="w-5 h-5 text-gray-500" />
                        </button>
                        <div className="hidden p-4 pt-0 text-gray-600">
                          <p>Our AI-powered system analyzes content using multiple reliable sources to verify its accuracy. It checks for context, source credibility, and cross-references claims with established facts.</p>
                        </div>
                      </div>
                      
                      <div className="border border-gray-200 rounded-lg">
                        <button
                          className="flex justify-between items-center w-full p-4 text-left"
                          onClick={(e) => {
                            e.currentTarget.setAttribute('aria-expanded', 
                              e.currentTarget.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'
                            );
                            e.currentTarget.nextElementSibling?.classList.toggle('hidden');
                          }}
                          aria-expanded="false"
                        >
                          <span className="font-medium text-gray-900">Is my data secure when I check content?</span>
                          <ChevronDown className="w-5 h-5 text-gray-500" />
                        </button>
                        <div className="hidden p-4 pt-0 text-gray-600">
                          <p>Yes, we take data security seriously. The content you submit is processed securely and not shared with third parties. We retain information only as long as necessary for the fact-checking process.</p>
                        </div>
                      </div>
                      
                      <div className="border border-gray-200 rounded-lg">
                        <button
                          className="flex justify-between items-center w-full p-4 text-left"
                          onClick={(e) => {
                            e.currentTarget.setAttribute('aria-expanded', 
                              e.currentTarget.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'
                            );
                            e.currentTarget.nextElementSibling?.classList.toggle('hidden');
                          }}
                          aria-expanded="false"
                        >
                          <span className="font-medium text-gray-900">How can I earn points and badges?</span>
                          <ChevronDown className="w-5 h-5 text-gray-500" />
                        </button>
                        <div className="hidden p-4 pt-0 text-gray-600">
                          <p>You can earn points by regularly checking content, completing learning modules, and participating in community discussions. Badges are awarded for specific achievements like completing a certain number of checks or maintaining high accuracy.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Contact Support</h3>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-gray-600 mb-4">If you need further assistance, our support team is ready to help.</p>
                      
                      <form onSubmit={(e) => {
                        e.preventDefault();
                        toast.success('Support request submitted. We\'ll get back to you soon.');
                      }}>
                        <div className="space-y-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Subject
                            </label>
                            <select className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500">
                              <option>Technical Issue</option>
                              <option>Account Question</option>
                              <option>Feature Request</option>
                              <option>Billing Question</option>
                              <option>Other</option>
                            </select>
                          </div>
                          
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Message
                            </label>
                            <textarea
                              rows={4}
                              placeholder="Describe your issue in detail..."
                              className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            ></textarea>
                          </div>
                          
                          <button 
                            type="submit"
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                          >
                            Submit Request
                          </button>
                        </div>
                      </form>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Resources</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <a href="#" className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                        <h4 className="font-medium text-blue-600 mb-1">User Guide</h4>
                        <p className="text-sm text-gray-600">Learn how to use all features effectively</p>
                      </a>
                      
                      <a href="#" className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                        <h4 className="font-medium text-blue-600 mb-1">Video Tutorials</h4>
                        <p className="text-sm text-gray-600">Step-by-step guides in video format</p>
                      </a>
                      
                      <a href="#" className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                        <h4 className="font-medium text-blue-600 mb-1">API Documentation</h4>
                        <p className="text-sm text-gray-600">For developers integrating with our platform</p>
                      </a>
                      
                      <a href="#" className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                        <h4 className="font-medium text-blue-600 mb-1">Blog & Updates</h4>
                        <p className="text-sm text-gray-600">Latest news and feature announcements</p>
                      </a>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
