// ===== 移动端导航菜单 =====
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

hamburger?.addEventListener('click', () => {
    navMenu.classList.toggle('active');
});

// 点击导航链接后关闭菜单
document.querySelectorAll('.nav-menu a').forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
    });
});

// ===== 导航栏滚动效果 =====
const navbar = document.querySelector('.navbar');
let lastScrollY = window.scrollY;

window.addEventListener('scroll', () => {
    const currentScrollY = window.scrollY;
    
    // 添加滚动阴影
    if (currentScrollY > 50) {
        navbar.style.background = 'rgba(15, 15, 26, 0.95)';
        navbar.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.3)';
    } else {
        navbar.style.background = 'rgba(15, 15, 26, 0.8)';
        navbar.style.boxShadow = 'none';
    }
    
    lastScrollY = currentScrollY;
});

// ===== 平滑滚动到锚点 =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const navHeight = navbar.offsetHeight;
            const targetPosition = target.offsetTop - navHeight - 20;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// ===== 导航栏高亮当前区域 =====
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-menu a');

const highlightNav = () => {
    const scrollY = window.scrollY;
    const navHeight = navbar.offsetHeight;
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop - navHeight - 100;
        const sectionHeight = section.offsetHeight;
        const sectionId = section.getAttribute('id');
        
        if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${sectionId}`) {
                    link.classList.add('active');
                }
            });
        }
    });
};

window.addEventListener('scroll', highlightNav);

// ===== 元素进入视口动画（class 驱动 + 交错延迟） =====
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
            revealObserver.unobserve(entry.target);
        }
    });
}, { root: null, rootMargin: '0px', threshold: 0.12 });

document.querySelectorAll('.about-grid, .platform-grid, .features-list').forEach(grid => {
    Array.from(grid.children).forEach((el, i) => {
        el.style.transitionDelay = (i * 0.08) + 's';
        revealObserver.observe(el);
    });
});

// ===== 通知提示 =====
function showNotification(message, type = 'success') {
    // 移除已存在的通知
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-icon">${type === 'success' ? '✓' : '✕'}</span>
        <span class="notification-message">${message}</span>
    `;
    
    // 添加样式
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'success' ? '#10b981' : '#ef4444'};
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 500;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        z-index: 9999;
        animation: slideDown 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        notification.style.animation = 'slideUp 0.3s ease-out forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateX(-50%) translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
    }
    
    @keyframes slideUp {
        from {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
        to {
            opacity: 0;
            transform: translateX(-50%) translateY(-20px);
        }
    }
`;
document.head.appendChild(style);

// ===== 代码窗口打字效果 =====
const codeElement = document.querySelector('.code-body code');
if (codeElement) {
    const originalCode = codeElement.innerHTML;
    
    // 添加闪烁光标效果
    const cursor = document.createElement('span');
    cursor.className = 'typing-cursor';
    cursor.textContent = '|';
    cursor.style.cssText = `
        animation: blink 1s step-end infinite;
        color: var(--primary);
    `;
    codeElement.appendChild(cursor);
    
    const blinkStyle = document.createElement('style');
    blinkStyle.textContent = `
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }
    `;
    document.head.appendChild(blinkStyle);
}

// ===== 平台卡片 3D 倾斜效果 =====
document.querySelectorAll('.platform-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 10;
        const rotateY = (centerX - x) / 10;
        
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(10px)`;
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = '';
    });
});

// ===== 粒子背景效果（可选）=====
function createParticle() {
    const particle = document.createElement('div');
    particle.style.cssText = `
        position: fixed;
        width: 4px;
        height: 4px;
        background: var(--primary);
        border-radius: 50%;
        pointer-events: none;
        opacity: 0.5;
        z-index: -1;
        left: ${Math.random() * 100}vw;
        top: ${Math.random() * 100}vh;
        animation: float-particle ${5 + Math.random() * 10}s linear infinite;
    `;
    
    document.body.appendChild(particle);
    
    setTimeout(() => particle.remove(), 15000);
}

// 每5秒创建一个粒子
setInterval(createParticle, 5000);

const particleStyle = document.createElement('style');
particleStyle.textContent = `
    @keyframes float-particle {
        0% {
            transform: translateY(100vh) rotate(0deg);
            opacity: 0;
        }
        10% {
            opacity: 0.5;
        }
        90% {
            opacity: 0.5;
        }
        100% {
            transform: translateY(-100vh) rotate(720deg);
            opacity: 0;
        }
    }
`;
document.head.appendChild(particleStyle);

// ===== 二维码弹窗 =====
const qrcodeModal = document.getElementById('qrcode-modal');
const qrcodeImg = document.getElementById('qrcode-img');
const qrcodeTriggers = document.querySelectorAll('[data-qrcode]');

qrcodeTriggers.forEach(trigger => {
    trigger.addEventListener('click', (e) => {
        e.preventDefault();
        const src = trigger.getAttribute('data-qrcode');
        if (src && qrcodeImg && qrcodeModal) {
            qrcodeImg.src = src;
            qrcodeModal.classList.add('active');
        }
    });
});

if (qrcodeModal) {
    qrcodeModal.addEventListener('click', (e) => {
        if (e.target === qrcodeModal || e.target.classList.contains('modal-close')) {
            qrcodeModal.classList.remove('active');
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && qrcodeModal.classList.contains('active')) {
            qrcodeModal.classList.remove('active');
        }
    });
}

// ===== 页面加载完成 =====
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
});

// ============================================================
// 炫彩升级特效
// ============================================================

// 顶部滚动进度条
const progressBar = document.querySelector('.scroll-progress');
if (progressBar) {
    const updateProgress = () => {
        const max = document.documentElement.scrollHeight - window.innerHeight;
        progressBar.style.width = (max > 0 ? (window.scrollY / max) * 100 : 0) + '%';
    };
    window.addEventListener('scroll', updateProgress, { passive: true });
    window.addEventListener('resize', updateProgress);
    updateProgress();
}

// Hero 鼠标聚光
const heroSection = document.querySelector('.hero');
const heroSpotlight = document.querySelector('.hero-spotlight');
if (heroSection && heroSpotlight && window.matchMedia('(hover: hover)').matches) {
    heroSection.addEventListener('pointermove', (e) => {
        const rect = heroSection.getBoundingClientRect();
        heroSpotlight.style.setProperty('--mx', (e.clientX - rect.left) + 'px');
        heroSpotlight.style.setProperty('--my', (e.clientY - rect.top) + 'px');
    });
}

// Hero 粒子网络背景
(function initParticles() {
    const canvas = document.querySelector('.hero-canvas');
    if (!canvas) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const ctx = canvas.getContext('2d');
    let particles = [];
    let w = 0;
    let h = 0;
    const LINK_DIST = 130;

    const buildParticles = () => {
        const count = window.innerWidth < 768 ? 26 : 64;
        particles = Array.from({ length: count }, () => ({
            x: Math.random() * w,
            y: Math.random() * h,
            vx: (Math.random() - 0.5) * 0.45,
            vy: (Math.random() - 0.5) * 0.45,
            r: Math.random() * 1.6 + 0.7
        }));
    };

    const resize = () => {
        const parent = canvas.parentElement;
        w = canvas.width = parent.offsetWidth;
        h = canvas.height = parent.offsetHeight;
        buildParticles();
    };

    const step = () => {
        if (!document.hidden) {
            ctx.clearRect(0, 0, w, h);

            particles.forEach((p) => {
                p.x += p.vx;
                p.y += p.vy;
                if (p.x < 0 || p.x > w) p.vx *= -1;
                if (p.y < 0 || p.y > h) p.vy *= -1;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(129, 140, 248, 0.75)';
                ctx.fill();
            });

            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const a = particles[i];
                    const b = particles[j];
                    const dx = a.x - b.x;
                    const dy = a.y - b.y;
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < LINK_DIST) {
                        ctx.strokeStyle = 'rgba(99, 102, 241, ' + (1 - dist / LINK_DIST) * 0.35 + ')';
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.moveTo(a.x, a.y);
                        ctx.lineTo(b.x, b.y);
                        ctx.stroke();
                    }
                }
            }
        }
        requestAnimationFrame(step);
    };

    resize();
    window.addEventListener('resize', resize);
    requestAnimationFrame(step);
})();

console.log('🚀 coder程 官方网站已加载完成！');
console.log('📧 欢迎订阅获取更多精彩内容');
