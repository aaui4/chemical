// المتغيرات العامة
let isPouring = false;
let animationEnabled = true;

// اختبار بسيط للون
console.log("✅ simulation.js loaded");
console.log("Config:", window.simulationConfig);



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

    // **هنا فقط نقوم بتشغيل الفقاعات إذا كان هناك غاز**
    setTimeout(() => {
        if (window.simulationConfig?.gasProduced == 1) {
            createBubbles();  // ستظهر فقط بعد بدء المحاكاة
        }
    }, 1300); 
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

    const totalQuantity = quantity1 + quantity2;

    let mixStep = 0;

    let mixInterval = setInterval(() => {

        mixStep += 0.1;

        if (mixStep <= 1) {

            // إنقاص مستوى الدورق الأيسر تدريجياً
            liquidLeft.style.height =
                (quantity1 * 12 * (1 - mixStep)) + 'px';

            // زيادة مستوى الدورق الأيمن تدريجياً
            const newHeight =
                (quantity2 + quantity1 * mixStep) * 12;

            liquidRight.style.height =
                Math.min(newHeight, 150) + 'px';

        } else {

            clearInterval(mixInterval);

            // الآن فقط نغيّر اللون مرة واحدة
            liquidRight.style.backgroundColor = finalColor;

            // نفرغ الدورق الأيسر
            liquidLeft.style.height = '0px';
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

    const config = window.simulationConfig;

    // غاز
    if (config?.gasProduced == 1) {
        createBubbles(liquidRight);
    }

    // راسب
    if (config?.precipitate == 1) {
        const layer = document.createElement('div');
        layer.className = 'precipitate-layer';
        layer.style.backgroundColor = config.resultColor;
        document.querySelector('#beakerRight .beaker-glass').appendChild(layer);
    }
}

// دالة إنشاء الفقاعات


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
    
}

// دالة تفعيل/تعطيل الحركة

function toggleAnimation() {
    animationEnabled = !animationEnabled;
    const toggleBtn = document.getElementById('toggleBtn');
    if (toggleBtn) {
        toggleBtn.innerHTML = animationEnabled ? '⚡ Disable Animation' : '🔌 Enable Animation';
    }
}
const config = window.simulationConfig || {};


document.addEventListener("DOMContentLoaded",function(){

const startBtn=document.getElementById("startBtn");

if(!startBtn) return;

startBtn.addEventListener("click",function(){

setTimeout(()=>{

startGasIfNeeded();

},1500);

});

});

// تشغيل المحاكاة عند تحميل الصفحة

