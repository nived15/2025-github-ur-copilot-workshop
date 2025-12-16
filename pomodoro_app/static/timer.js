// Pomodoro Timer JavaScript Implementation

class PomodoroTimer {
    constructor() {
        // Timer state
        this.isRunning = false;
        this.isPaused = false;
        this.currentTime = 0; // in seconds
        this.intervalId = null;
        
        // Session management
        this.currentSession = 1;
        this.maxSessions = 4;
        this.sessionType = 'work'; // 'work', 'short_break', 'long_break'
        
        // Duration settings (in seconds)
        this.settings = {
            workDuration: 25 * 60,
            shortBreakDuration: 5 * 60,
            longBreakDuration: 15 * 60
        };
        
        // DOM elements
        this.initializeElements();
        this.loadSettings();
        this.loadTheme();
        this.resetTimer();
        this.bindEvents();
    }
    
    initializeElements() {
        this.timerTimeEl = document.getElementById('timer-time');
        this.timerStatusEl = document.getElementById('timer-status');
        this.sessionTypeEl = document.getElementById('session-type');
        this.sessionCountEl = document.getElementById('session-count');
        this.timerCircleEl = document.querySelector('.timer-circle');
        this.progressDotsEl = document.getElementById('progress-dots');
        
        // Buttons
        this.startBtn = document.getElementById('start-btn');
        this.resetBtn = document.getElementById('reset-btn');
        this.skipBtn = document.getElementById('skip-btn');
        this.settingsBtn = document.getElementById('settings-btn');
        this.themeToggleBtn = document.getElementById('theme-toggle-btn');
        
        // Settings panel
        this.settingsPanel = document.getElementById('settings-panel');
        this.workDurationInput = document.getElementById('work-duration');
        this.shortBreakInput = document.getElementById('short-break-duration');
        this.longBreakInput = document.getElementById('long-break-duration');
        this.saveSettingsBtn = document.getElementById('save-settings-btn');
        this.cancelSettingsBtn = document.getElementById('cancel-settings-btn');
    }
    
    loadSettings() {
        // Load settings from localStorage if available
        const saved = localStorage.getItem('pomodoroSettings');
        if (saved) {
            const settings = JSON.parse(saved);
            this.settings.workDuration = settings.workDuration * 60;
            this.settings.shortBreakDuration = settings.shortBreakDuration * 60;
            this.settings.longBreakDuration = settings.longBreakDuration * 60;
        }
        
        // Update input fields
        this.workDurationInput.value = Math.floor(this.settings.workDuration / 60);
        this.shortBreakInput.value = Math.floor(this.settings.shortBreakDuration / 60);
        this.longBreakInput.value = Math.floor(this.settings.longBreakDuration / 60);
    }
    
    saveSettings() {
        const settings = {
            workDuration: parseInt(this.workDurationInput.value),
            shortBreakDuration: parseInt(this.shortBreakInput.value),
            longBreakDuration: parseInt(this.longBreakInput.value)
        };
        
        this.settings.workDuration = settings.workDuration * 60;
        this.settings.shortBreakDuration = settings.shortBreakDuration * 60;
        this.settings.longBreakDuration = settings.longBreakDuration * 60;
        
        localStorage.setItem('pomodoroSettings', JSON.stringify(settings));
        this.hideSettings();
        this.resetTimer();
    }
    
    bindEvents() {
        this.startBtn.addEventListener('click', () => this.toggleTimer());
        this.resetBtn.addEventListener('click', () => this.resetTimer());
        this.skipBtn.addEventListener('click', () => this.skipSession());
        this.settingsBtn.addEventListener('click', () => this.showSettings());
        this.saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        this.cancelSettingsBtn.addEventListener('click', () => this.hideSettings());
        this.themeToggleBtn.addEventListener('click', () => this.toggleTheme());
    }
    
    getCurrentDuration() {
        if (this.sessionType === 'work') {
            return this.settings.workDuration;
        } else if (this.sessionType === 'short_break') {
            return this.settings.shortBreakDuration;
        } else {
            return this.settings.longBreakDuration;
        }
    }
    
    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    updateDisplay() {
        this.timerTimeEl.textContent = this.formatTime(this.currentTime);
        
        // Update session info
        if (this.sessionType === 'work') {
            this.sessionTypeEl.textContent = 'Work Session';
            this.sessionCountEl.textContent = `Session ${this.currentSession} of ${this.maxSessions}`;
            this.timerCircleEl.className = 'timer-circle active';
        } else if (this.sessionType === 'short_break') {
            this.sessionTypeEl.textContent = 'Short Break';
            this.sessionCountEl.textContent = `After Session ${this.currentSession - 1}`;
            this.timerCircleEl.className = 'timer-circle break';
        } else {
            this.sessionTypeEl.textContent = 'Long Break';
            this.sessionCountEl.textContent = `After ${this.maxSessions} Sessions`;
            this.timerCircleEl.className = 'timer-circle break';
        }
        
        // Update status
        if (!this.isRunning && this.currentTime === this.getCurrentDuration()) {
            this.timerStatusEl.textContent = 'Ready to start';
        } else if (this.isRunning) {
            this.timerStatusEl.textContent = 'Focus time';
        } else if (this.isPaused) {
            this.timerStatusEl.textContent = 'Paused';
        } else {
            this.timerStatusEl.textContent = 'Ready';
        }
        
        // Update progress dots
        this.updateProgressDots();
    }
    
    updateProgressDots() {
        const dots = this.progressDotsEl.querySelectorAll('.dot');
        dots.forEach((dot, index) => {
            const sessionNum = index + 1;
            if (sessionNum < this.currentSession) {
                dot.className = 'dot completed';
            } else if (sessionNum === this.currentSession && this.sessionType === 'work') {
                dot.className = 'dot active';
            } else {
                dot.className = 'dot';
            }
        });
    }
    
    toggleTimer() {
        if (this.isRunning) {
            this.pauseTimer();
        } else {
            this.startTimer();
        }
    }
    
    startTimer() {
        this.isRunning = true;
        this.isPaused = false;
        this.startBtn.textContent = 'Pause';
        
        this.intervalId = setInterval(() => {
            if (this.currentTime > 0) {
                this.currentTime--;
                this.updateDisplay();
            } else {
                this.completeSession();
            }
        }, 1000);
        
        this.updateDisplay();
    }
    
    pauseTimer() {
        this.isRunning = false;
        this.isPaused = true;
        this.startBtn.textContent = 'Start';
        
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        
        this.updateDisplay();
    }
    
    resetTimer() {
        this.isRunning = false;
        this.isPaused = false;
        this.startBtn.textContent = 'Start';
        
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        
        this.currentTime = this.getCurrentDuration();
        this.updateDisplay();
    }
    
    async completeSession() {
        this.pauseTimer();
        
        // Log the completed session
        await this.logSession('completed');
        
        // Play notification sound (optional - browser notification)
        this.showNotification(`${this.sessionType === 'work' ? 'Work session' : 'Break'} completed!`);
        
        // Move to next session
        this.nextSession();
    }
    
    async skipSession() {
        if (this.isRunning || this.isPaused) {
            this.pauseTimer();
            
            // Log the skipped session
            await this.logSession('skipped');
            
            // Move to next session
            this.nextSession();
        }
    }
    
    nextSession() {
        if (this.sessionType === 'work') {
            // After work session
            if (this.currentSession >= this.maxSessions) {
                // Long break after 4 sessions
                this.sessionType = 'long_break';
            } else {
                // Short break
                this.sessionType = 'short_break';
            }
        } else {
            // After break, start next work session
            if (this.sessionType === 'short_break') {
                this.currentSession++;
            } else if (this.sessionType === 'long_break') {
                this.currentSession = 1; // Reset for next cycle
            }
            this.sessionType = 'work';
        }
        
        this.resetTimer();
    }
    
    async logSession(action) {
        try {
            const sessionData = {
                session_type: this.sessionType,
                action: action,
                session_number: this.currentSession
            };
            
            const response = await fetch('/log', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(sessionData)
            });
            
            if (!response.ok) {
                console.error('Failed to log session:', response.statusText);
            }
        } catch (error) {
            console.error('Error logging session:', error);
        }
    }
    
    showNotification(message) {
        // Browser notification
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Pomodoro Timer', {
                body: message,
                icon: '/static/favicon.ico' // Optional
            });
        } else if ('Notification' in window && Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    new Notification('Pomodoro Timer', {
                        body: message,
                        icon: '/static/favicon.ico'
                    });
                }
            });
        }
        
        // Visual notification (simple alert for now)
        // You could replace this with a custom modal
        setTimeout(() => {
            alert(message);
        }, 100);
    }
    
    showSettings() {
        this.settingsPanel.style.display = 'block';
    }
    
    hideSettings() {
        this.settingsPanel.style.display = 'none';
    }
    
    loadTheme() {
        // Load theme preference from localStorage
        const savedTheme = localStorage.getItem('pomodoroTheme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
            this.updateThemeIcon('light');
        } else {
            document.body.classList.remove('dark-theme');
            this.updateThemeIcon('dark');
        }
    }
    
    toggleTheme() {
        // Toggle dark theme class on body
        document.body.classList.toggle('dark-theme');
        
        // Save preference to localStorage
        const isDark = document.body.classList.contains('dark-theme');
        localStorage.setItem('pomodoroTheme', isDark ? 'dark' : 'light');
        
        // Update icon
        this.updateThemeIcon(isDark ? 'light' : 'dark');
    }
    
    updateThemeIcon(theme) {
        // Update the theme toggle button icon
        const themeIcon = this.themeToggleBtn.querySelector('.theme-icon');
        if (themeIcon) {
            themeIcon.textContent = theme === 'dark' ? '🌙' : '☀️';
        }
    }
}

// Initialize the timer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new PomodoroTimer();
});