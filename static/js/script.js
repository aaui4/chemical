const temp = document.getElementById("temperature");
const tempValue = document.getElementById("tempValue");
temp.addEventListener("input", () => {
  tempValue.textContent = temp.value;
});

const pressure = document.getElementById("pressure");
const pressureValue = document.getElementById("pressureValue");
pressure.addEventListener("input", () => {
  pressureValue.textContent = pressure.value;
});

const startBtn = document.getElementById("startReaction");
const reactantsDiv = document.querySelector(".reactants");
const flameDiv = document.querySelector(".flame");
const productsDiv = document.querySelector(".products");

startBtn.addEventListener("click", () => {
  // مرحلة المواد
  reactantsDiv.style.display = "block";
  flameDiv.style.display = "none";
  productsDiv.style.display = "none";

  setTimeout(() => {
    // مرحلة الاشتعال
    reactantsDiv.style.display = "none";
    flameDiv.style.display = "block";
  }, 2000);

  setTimeout(() => {
    // مرحلة النواتج
    flameDiv.style.display = "none";
    productsDiv.style.display = "block";
  }, 4000);
});