'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { motion } from 'framer-motion';

const fadeInUp = {
  initial: { opacity: 0, y: 60 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 }
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.2
    }
  }
};

export default function LandingPageClient() {
  return (
    <div className="min-h-screen bg-[#0B0B0B] relative overflow-hidden">
      {/* Animated background with subtle red grid pattern */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-[#0B0B0B] via-[#111111] to-[#0B0B0B]" />
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+CiAgPHJlY3Qgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBmaWxsPSJub25lIiBzdHJva2U9IiNFRTU1NTUiIHN0cm9rZS1vcGFjaXR5PSIwLjEiIHN0cm9rZS13aWR0aD0iMSIvPgo8L3N2Zz4K')] opacity-20" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.header
          className="py-6 flex items-center justify-between"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-2xl font-bold text-[#E25555]">
            AI Todo ChatBot
          </h1>
          <div className="flex items-center gap-3">
            <Link href="/signin">
              <Button variant="ghost" size="sm" className="border border-[#E25555] text-[#E25555] hover:bg-[#E25555]/10">
                Sign In
              </Button>
            </Link>
            <Link href="/signup">
              <Button variant="ghost" size="sm" className="border border-[#E25555] text-[#E25555] hover:bg-[#E25555]/10">
                Sign Up
              </Button>
            </Link>
          </div>
        </motion.header>

        {/* Hero section */}
        <motion.div
          className="py-20 md:py-12 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          <motion.div
            className="inline-block mb-6 px-4 py-2 border border-[#E25555]/30 rounded-full backdrop-blur-sm"
            {...fadeInUp}
            transition={{ delay: 0.2 }}
          >
            <span className="text-sm font-medium text-[#E25555]">🤖 AI-Powered Productivity</span>
          </motion.div>

          <motion.h2
            className="text-4xl md:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight"
            {...fadeInUp}
            transition={{ delay: 0.3 }}
          >
            Manage Tasks Smarter
            <br />
            <span className="text-[#E25555]">
              with AI
            </span>
          </motion.h2>

          <motion.p
            className="text-lg md:text-xl text-gray-300 mb-10 max-w-2xl mx-auto leading-relaxed"
            {...fadeInUp}
            transition={{ delay: 0.4 }}
          >
            Create, update, and organize your tasks manually or with an AI-powered chatbot.
            Transform your productivity with intelligent task management.
          </motion.p>

          <motion.div
            className="flex items-center justify-center gap-4 flex-wrap"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            <Link href="/signup">
              <Button 
                variant="ghost" 
                size="lg" 
                className="border-2 border-[#E25555] text-[#E25555] hover:bg-[#E25555]/10 hover:shadow-[0_0_15px_rgba(226,85,85,0.3)]"
              >
                Start Using AI Todo App
              </Button>
            </Link>
            <Link href="#features">
              <Button 
                variant="ghost" 
                size="lg" 
                className="text-[#E25555] hover:bg-[#E25555]/10"
              >
                View Features
              </Button>
            </Link>
          </motion.div>
        </motion.div>

        {/* Features section */}
        <motion.section
          className="py-16"
          id="features"
          initial="initial"
          whileInView="animate"
          viewport={{ once: true, amount: 0.2 }}
          variants={staggerContainer}
        >
          <motion.h2
            className="text-3xl md:text-4xl font-bold text-center text-white mb-12"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            Powerful Features
          </motion.h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            <motion.div
              className="bg-transparent rounded-xl p-6 border-2 border-[#E25555] hover:border-[#E25555]/70 transition-all duration-300 hover:shadow-[0_0_20px_rgba(226,85,85,0.2)]"
              variants={fadeInUp}
              whileHover={{ y: -10 }}
            >
              <div className="w-12 h-12 rounded-lg flex items-center justify-center mb-4 border border-[#E25555]">
                <span className="text-[#E25555] text-xl">🤖</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">
                AI Powered Todo ChatBot
              </h3>
              <p className="text-gray-400">
                Generate, manage, and organize tasks using our intelligent AI assistant.
              </p>
            </motion.div>

            <motion.div
              className="bg-transparent rounded-xl p-6 border-2 border-[#E25555] hover:border-[#E25555]/70 transition-all duration-300 hover:shadow-[0_0_20px_rgba(226,85,85,0.2)]"
              variants={fadeInUp}
              whileHover={{ y: -10 }}
            >
              <div className="w-12 h-12 rounded-lg flex items-center justify-center mb-4 border border-[#E25555]">
                <span className="text-[#E25555] text-xl">✍️</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Manual Task Creation
              </h3>
              <p className="text-gray-400">
                Create and manage tasks manually with our intuitive interface.
              </p>
            </motion.div>

            <motion.div
              className="bg-transparent rounded-xl p-6 border-2 border-[#E25555] hover:border-[#E25555]/70 transition-all duration-300 hover:shadow-[0_0_20px_rgba(226,85,85,0.2)]"
              variants={fadeInUp}
              whileHover={{ y: -10 }}
            >
              <div className="w-12 h-12 rounded-lg flex items-center justify-center mb-4 border border-[#E25555]">
                <span className="text-[#E25555] text-xl">🔄</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Update, Complete & Delete Tasks
              </h3>
              <p className="text-gray-400">
                Full control over your tasks with update, complete, and delete options.
              </p>
            </motion.div>

            <motion.div
              className="bg-transparent rounded-xl p-6 border-2 border-[#E25555] hover:border-[#E25555]/70 transition-all duration-300 hover:shadow-[0_0_20px_rgba(226,85,85,0.2)]"
              variants={fadeInUp}
              whileHover={{ y: -10 }}
            >
              <div className="w-12 h-12 rounded-lg flex items-center justify-center mb-4 border border-[#E25555]">
                <span className="text-[#E25555] text-xl">⚡</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Fast, Clean & Distraction-Free UI
              </h3>
              <p className="text-gray-400">
                Focus on what matters with our clean and distraction-free interface.
              </p>
            </motion.div>
          </div>
        </motion.section>

        {/* Interface Preview */}
        <motion.section
          className="py-16"
          id="preview"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <motion.h2
            className="text-3xl md:text-4xl font-bold text-center text-white mb-12"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            AI-Powered Task Management
          </motion.h2>

          <div className="max-w-4xl mx-auto bg-[#111111] rounded-xl border-2 border-[#E25555] p-6">
            <div className="flex flex-col md:flex-row gap-8">
              <div className="md:w-1/2">
                <div className="bg-[#0B0B0B] rounded-lg border border-[#E25555]/30 p-4 mb-4">
                  <div className="flex items-center mb-3">
                    <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-start">
                      <input type="checkbox" className="mt-1 mr-2 rounded border-[#E25555] bg-transparent" />
                      <div className="flex-1">
                        <p className="text-white">Complete project proposal</p>
                        <p className="text-gray-400 text-sm">Due: Tomorrow</p>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <input type="checkbox" className="mt-1 mr-2 rounded border-[#E25555] bg-transparent" />
                      <div className="flex-1">
                        <p className="text-white">Schedule team meeting</p>
                        <p className="text-gray-400 text-sm">Due: Today</p>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <input type="checkbox" defaultChecked className="mt-1 mr-2 rounded border-[#E25555] bg-transparent line-through" />
                      <div className="flex-1">
                        <p className="text-gray-500 line-through">Review quarterly reports</p>
                        <p className="text-gray-400 text-sm">Completed</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="md:w-1/2">
                <div className="bg-[#0B0B0B] rounded-lg border border-[#E25555]/30 p-4">
                  <div className="font-bold text-[#E25555] mb-3">AI Assistant</div>
                  <div className="space-y-3">
                    <div className="bg-[#1a1a1a] rounded-lg p-3 border border-[#E25555]/20">
                      <p className="text-gray-300 text-sm">"Create a task to schedule the client meeting for next week"</p>
                    </div>
                    <div className="bg-[#1a1a1a] rounded-lg p-3 border border-[#E25555]/20">
                      <p className="text-gray-300 text-sm">"Mark the project proposal as completed"</p>
                    </div>
                    <div className="bg-[#1a1a1a] rounded-lg p-3 border border-[#E25555]/20">
                      <p className="text-gray-300 text-sm">"What tasks are due today?"</p>
                    </div>
                    <div className="flex mt-2">
                      <input 
                        type="text" 
                        placeholder="Ask AI to manage tasks..." 
                        className="flex-1 bg-[#1a1a1a] border border-[#E25555]/30 rounded-l-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-[#E25555]"
                      />
                      <button className="bg-[#E25555] text-white px-4 py-2 rounded-r-lg hover:bg-[#E25555]/90">
                        Send
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* How It Works */}
        <motion.section
          className="py-16"
          id="how-it-works"
          initial="initial"
          whileInView="animate"
          viewport={{ once: true, amount: 0.2 }}
          variants={staggerContainer}
        >
          <motion.h2
            className="text-3xl md:text-4xl font-bold text-center text-white mb-12"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            How It Works
          </motion.h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <motion.div
              className="text-center"
              variants={fadeInUp}
            >
              <div className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-[#E25555]">
                <span className="text-[#E25555] text-xl font-bold">1</span>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Create tasks manually or ask the AI chatbot</h3>
              <p className="text-gray-400">
                Add tasks yourself or simply tell our AI assistant what you need to do.
              </p>
            </motion.div>
            
            <motion.div
              className="text-center"
              variants={fadeInUp}
            >
              <div className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-[#E25555]">
                <span className="text-[#E25555] text-xl font-bold">2</span>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Update, complete, or delete tasks anytime</h3>
              <p className="text-gray-400">
                Manage your tasks with simple controls and keep everything organized.
              </p>
            </motion.div>
            
            <motion.div
              className="text-center"
              variants={fadeInUp}
            >
              <div className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 border-2 border-[#E25555]">
                <span className="text-[#E25555] text-xl font-bold">3</span>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Stay organized and productive every day</h3>
              <p className="text-gray-400">
                Focus on what matters most and achieve your goals efficiently.
              </p>
            </motion.div>
          </div>
        </motion.section>

        {/* CTA Section */}
        <motion.div
          className="py-20 my-16 rounded-3xl border border-[#E25555]/30 bg-[#0B0B0B]/50 backdrop-blur-sm"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <div className="text-center max-w-3xl mx-auto px-4">
            <motion.h2
              className="text-3xl md:text-4xl font-bold text-white mb-6"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              Let AI Organize Your Day
            </motion.h2>
            <motion.p
              className="text-lg text-gray-300 mb-8"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2, duration: 0.6 }}
            >
              Join thousands of users who have transformed their productivity with our AI-powered task manager.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4, duration: 0.6 }}
            >
              <Link href="/signup">
                <Button 
                variant="ghost" 
                size="lg" 
                className="border-2 border-[#E25555] text-[#E25555] hover:bg-[#E25555]/10 hover:shadow-[0_0_20px_rgba(226,85,85,0.3)] text-lg px-8 py-4"
              >
                Start Using AI Todo App
                </Button>
              </Link>
            </motion.div>
          </div>
        </motion.div>

        {/* Footer */}
        <footer className="py-8 text-center text-sm text-gray-500 border-t border-[#E25555]/30">
          <motion.div
            className="mb-4"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            <h3 className="text-xl font-bold text-[#E25555] mb-2">
              ✨ AI Todo ChatBot
            </h3>
            <p className="text-gray-400">AI-Powered Task Management</p>
          </motion.div>
          <motion.div
            className="flex justify-center space-x-6 mb-4"
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            <a href="https://www.youtube.com/@subhankaladi" className="text-gray-400 hover:text-[#E25555] transition-colors">
              <span className="sr-only">Youtube</span>
              <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path fillRule="evenodd" d="M2 5a2 2 0 012-2h11a3 3 0 110 6H4.5A1.5 1.5 0 003 10.5V13H2a2 2 0 01-2-2V5zm14 0a2 2 0 012-2h2a2 2 0 012 2v10a2 2 0 01-2 2h-2a2 2 0 01-2-2V5z" clipRule="evenodd" />
              </svg>
            </a>
            <a href="https://github.com/subhankaladi" className="text-gray-400 hover:text-[#E25555] transition-colors">
              <span className="sr-only">GitHub</span>
              <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
              </svg>
            </a>
            <a href="https://www.linkedin.com/in/subhankaladi" className="text-gray-400 hover:text-[#E25555] transition-colors">
              <span className="sr-only">Contact</span>
              <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
              </svg>
            </a>
          </motion.div>
          <motion.p
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.6, duration: 0.6 }}
          >
            &copy; 2026 AI Todo ChatBot. All rights reserved.
          </motion.p>
        </footer>
      </div>
    </div>
  );
}