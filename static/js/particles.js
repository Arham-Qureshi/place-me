(function () {
    'use strict';

    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const CFG = {
        count: 90,               // number of particles
        speed: 0.45,             // max drift speed
        minRadius: 1.2,
        maxRadius: 2.8,
        connectDist: 130,        // px — draw line when closer than this
        repelDist: 110,          // px — mouse repel radius
        repelStrength: 3.5,      // push force
        lineOpacityMax: 0.22,    // max line alpha
        particleOpacity: 0.65,
        // brand palette
        colors: ['#7a7ba2ff', '#4d0313ff', '#2c432eff', '#a20d75ff', '#649994ff'],
        bg: '#d9e8e7ff',           // very light mint — replaces gradient
    };

    let W, H, particles = [];
    const mouse = { x: -9999, y: -9999 };

    function resize() {
        W = canvas.width = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }

    function createParticle() {
        const angle = Math.random() * Math.PI * 2;
        const speed = (Math.random() * CFG.speed) + 0.1;
        return {
            x: Math.random() * W,
            y: Math.random() * H,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            r: CFG.minRadius + Math.random() * (CFG.maxRadius - CFG.minRadius),
            color: CFG.colors[Math.floor(Math.random() * CFG.colors.length)],
        };
    }

    function initParticles() {
        particles = [];
        for (let i = 0; i < CFG.count; i++) particles.push(createParticle());
    }

    function drawParticle(p) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = CFG.particleOpacity;
        ctx.fill();
        ctx.globalAlpha = 1;
    }

    function drawLine(p1, p2, dist) {
        const alpha = CFG.lineOpacityMax * (1 - dist / CFG.connectDist);
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = p1.color;
        ctx.globalAlpha = alpha;
        ctx.lineWidth = 0.8;
        ctx.stroke();
        ctx.globalAlpha = 1;
    }

    function drawMouseLines() {
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            const dx = mouse.x - p.x;
            const dy = mouse.y - p.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < CFG.connectDist * 1.2) {
                const alpha = CFG.lineOpacityMax * 0.7 * (1 - dist / (CFG.connectDist * 1.2));
                ctx.beginPath();
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(mouse.x, mouse.y);
                ctx.strokeStyle = '#10b981';
                ctx.globalAlpha = alpha;
                ctx.lineWidth = 0.6;
                ctx.stroke();
                ctx.globalAlpha = 1;
            }
        }
    }

    function update(p) {
        const dx = p.x - mouse.x;
        const dy = p.y - mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < CFG.repelDist && dist > 0) {
            const force = (CFG.repelDist - dist) / CFG.repelDist;
            p.vx += (dx / dist) * force * CFG.repelStrength * 0.05;
            p.vy += (dy / dist) * force * CFG.repelStrength * 0.05;
        }

        const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
        const maxSpeed = CFG.speed * 3;
        if (speed > maxSpeed) {
            p.vx = (p.vx / speed) * maxSpeed;
            p.vy = (p.vy / speed) * maxSpeed;
        }

        const naturalSpeed = 0.3;
        if (speed > naturalSpeed) {
            p.vx *= 0.98;
            p.vy *= 0.98;
        }

        p.x += p.vx;
        p.y += p.vy;

        if (p.x < -10) p.x = W + 10;
        if (p.x > W + 10) p.x = -10;
        if (p.y < -10) p.y = H + 10;
        if (p.y > H + 10) p.y = -10;
    }

    function frame() {
        ctx.fillStyle = CFG.bg;
        ctx.fillRect(0, 0, W, H);
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < CFG.connectDist) drawLine(particles[i], particles[j], dist);
            }
        }

        drawMouseLines();

        for (let i = 0; i < particles.length; i++) {
            update(particles[i]);
            drawParticle(particles[i]);
        }

        requestAnimationFrame(frame);
    }

    window.addEventListener('resize', () => { resize(); initParticles(); });
    window.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });
    window.addEventListener('mouseleave', () => { mouse.x = -9999; mouse.y = -9999; });

    resize();
    initParticles();
    frame();
}());
