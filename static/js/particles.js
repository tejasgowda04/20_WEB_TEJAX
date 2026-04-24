// Animated particle background
(function(){
  const container = document.getElementById('particles');
  if(!container) return;
  const colors = ['#667eea','#764ba2','#f59e0b','#10b981','#3b82f6','#8b5cf6'];
  for(let i=0;i<40;i++){
    const p = document.createElement('div');
    p.className='particle';
    const size = Math.random()*5+2;
    const color = colors[Math.floor(Math.random()*colors.length)];
    p.style.cssText=`
      width:${size}px;height:${size}px;
      background:${color};
      left:${Math.random()*100}%;
      animation-duration:${Math.random()*15+10}s;
      animation-delay:${Math.random()*10}s;
      filter:blur(${Math.random()>0.5?'1px':'0'});
    `;
    container.appendChild(p);
  }
})();
