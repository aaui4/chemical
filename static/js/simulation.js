// المتغيرات العامة
let isPouring = false;
let animationEnabled = true;

// اختبار بسيط للون
console.log("✅ simulation.js loaded");
console.log("Config:", window.simulationConfig);

// اختبار تغيير اللون مباشرة
window.addEventListener('load', function() {
    console.log("Testing color change...");
    const liquidRight = document.getElementById('liquidRight');
    if (liquidRight) {
        const testColor = window.simulationConfig?.resultColor || 'red';
        liquidRight.style.backgroundColor = testColor;
        console.log("Color changed to:", testColor);
    } else {
        console.error("liquidRight not found!");
    }
});

// دالة بدء التفاعل

function startPouring() {
    // التحقق من التكرار والتفعيل
    if (isPouring || !animationEnabled) return;
    
    isPouring = true;
    
    // الحصول على العناصر
    const elements = getElements();
    if (!elements) return;
    
    const { beakerLeft, liquidLeft, liquidRight, liquidStream, startBtn } = elements;
    
    // تغيير نص الزر
    startBtn.innerHTML = '⏳ Pouring...';
    
    // حساب موضع تيار السائل
    const leftRect = beakerLeft.getBoundingClientRect();
    const sceneRect = document.querySelector('.lab-scene').getBoundingClientRect();
    
    // إظهار تيار السائل
    showLiquidStream(liquidStream, leftRect, sceneRect);
    
    // بدء حركة السكب
    startPouringAnimation(liquidStream, liquidRight, liquidLeft, beakerLeft, startBtn);
}

// دالة الحصول على العناصر
function getElements() {
    const elements = {
        beakerLeft: document.getElementById('beakerLeft'),
        beakerRight: document.getElementById('beakerRight'),
        liquidLeft: document.getElementById('liquidLeft'),
        liquidRight: document.getElementById('liquidRight'),
        liquidStream: document.getElementById('liquidStream'),
        startBtn: document.getElementById('startBtn'),
        toggleBtn: document.getElementById('toggleBtn')
    };
    
    // التحقق من وجود جميع العناصر
    for (let [key, value] of Object.entries(elements)) {
        if (!value && key !== 'toggleBtn') {
            console.error(`❌ Element not found: ${key}`);
            return null;
        }
    }
    
    return elements;
}

// دالة إظهار تيار السائل
function showLiquidStream(liquidStream, leftRect, sceneRect) {
    liquidStream.style.display = 'block';
    liquidStream.style.left = (leftRect.right - sceneRect.left - 8) + 'px';
    liquidStream.style.top = (leftRect.top - sceneRect.top + 60) + 'px';
    liquidStream.style.height = '0px';
}

// دالة حركة السكب

function startPouringAnimation(liquidStream, liquidRight, liquidLeft, beakerLeft, startBtn) {
    let streamHeight = 0;
    
    // تكبير تيار السائل تدريجياً
    const streamInterval = setInterval(() => {
        if (streamHeight < 80) {
            streamHeight += 5;
            liquidStream.style.height = streamHeight + 'px';
        }
    }, 50);
    
    // بعد 1.3 ثانية، نبدأ في تغيير لون السائل
    setTimeout(() => {
        changeLiquidColor(liquidRight, liquidLeft);
    }, 1300);
    
    // بعد 2.4 ثانية، ننهي الحركة
    setTimeout(() => {
        finishPouring(streamInterval, liquidStream, beakerLeft, startBtn, liquidRight);
    }, 2400);
}

// دالة تغيير لون السائل
function changeLiquidColor(liquidRight, liquidLeft) {
    const config = window.simulationConfig;
    const finalColor = config?.resultColor || 'transparent';
    const quantity1 = config?.quantity1 || 0;
    const quantity2 = config?.quantity2 || 0;
    
    let mixStep = 0;
    let mixInterval = setInterval(() => {
        mixStep += 0.1;
        if (mixStep <= 1) {
            // تغيير اللون
            liquidRight.style.backgroundColor = finalColor;
            
            // تغيير الارتفاع
            const newHeight = (quantity2 + quantity1 * mixStep) * 12;
            liquidRight.style.height = Math.min(newHeight, 150) + 'px';
        } else {
            clearInterval(mixInterval);
            liquidLeft.style.height = '0px'; // تفريغ الدورق الأيسر
        }
    }, 100);
}


// دالة إنهاء السكب

function finishPouring(streamInterval, liquidStream, beakerLeft, startBtn, liquidRight) {
    clearInterval(streamInterval);
    liquidStream.style.display = 'none';
    beakerLeft.style.transform = 'translateY(0)';
    isPouring = false;
    startBtn.innerHTML = '🔬 Start Reaction';
    
    // إضافة فقاعات إذا كان هناك غاز
    const config = window.simulationConfig;
    if (config?.gasProduced == 1) {
        createBubbles(liquidRight);
    }
}

// دالة إنشاء الفقاعات
function createBubbles(liquidRight) {
    const beakerGlass = document.querySelector('#beakerRight .beaker-glass');
    if (!beakerGlass) return;
    
    for (let i = 0; i < 5; i++) {
        setTimeout(() => {
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.style.left = Math.random() * 70 + 15 + '%';
            bubble.style.width = Math.random() * 6 + 3 + 'px';
            bubble.style.height = bubble.style.width;
            beakerGlass.appendChild(bubble);
            
            setTimeout(() => bubble.remove(), 1500);
        }, i * 300);
    }
}

// دالة إعادة التشغيل

function resetSimulation() {
    const elements = getElements();
    if (!elements) return;
    
    const { liquidLeft, liquidRight, liquidStream, beakerLeft, startBtn } = elements;
    const config = window.simulationConfig;
    
    // إعادة القيم الأصلية
    liquidLeft.style.height = (config?.quantity1 * 12) + 'px';
    liquidLeft.style.backgroundColor = config?.reactant1Color || 'transparent';
    liquidRight.style.height = (config?.quantity2 * 12) + 'px';
    liquidRight.style.backgroundColor = config?.reactant2Color || 'transparent';
    
    // إخفاء التيار وإعادة الزر
    liquidStream.style.display = 'none';
    beakerLeft.style.transform = 'translateY(0)';
    startBtn.innerHTML = '🔬 Start Reaction';
    
    // إعادة المتغيرات
    isPouring = false;
    
    // إزالة الفقاعات الزائدة
    document.querySelectorAll('#beakerRight .beaker-glass .bubble').forEach(b => b.remove());
}

// دالة تفعيل/تعطيل الحركة

function toggleAnimation() {
    animationEnabled = !animationEnabled;
    const toggleBtn = document.getElementById('toggleBtn');
    if (toggleBtn) {
        toggleBtn.innerHTML = animationEnabled ? '⚡ Disable Animation' : '🔌 Enable Animation';
    }
}

// تشغيل المحاكاة عند تحميل الصفحة

window.addEventListener('load', function() {
    console.log("✅ Page loaded, starting simulation...");
    console.log("Config:", window.simulationConfig);
    
    setTimeout(() => {
        if (animationEnabled) {
            startPouring();
        }
    }, 800);
});