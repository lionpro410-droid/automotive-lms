// static/js/anti_cheat.js
document.addEventListener("DOMContentLoaded", function () {
    let examSubmitted = false;

    // ስክሪኑ ሲጠፋ ወይም ተማሪው ወደ ሌላ አፕ / ታብ ሲሄድ
    document.addEventListener("visibilitychange", function () {
        if (document.hidden && !examSubmitted) {
            triggerAutoSubmit("ማስጠንቀቂያ! ስልኮን ሎክ በማድረግዎ ወይም ከፈተናው ገጽ በመውጣትዎ ምክንያት ፈተናዎ በራስ ሰር ተዘግቷል።");
        }
    });

    // መስኮቱ ፎከስ ሲያጣ (Window Blur)
    window.addEventListener("blur", function () {
        if (!examSubmitted) {
            triggerAutoSubmit("ማስጠንቀቂያ! ከፈተናው ማዕቀፍ ውጭ ሌላ መተግበሪያ በመክፈትዎ ፈተናዎ ተሰርዟል።");
        }
    });

    function triggerAutoSubmit(message) {
        if (examSubmitted) return;
        examSubmitted = true;
        
        alert(message);
        
        const examForm = document.getElementById('examForm'); 
        if (examForm) {
            examForm.submit();
        } else {
            window.location.href = "/student"; 
        }
    }
});