from ui import BackgroundRemoverUI
from ai_engine import BgRemoverAI

if __name__ == "__main__":
    # Yapay zeka motorunu başlat
    ai_engine = BgRemoverAI()
    
    # Motoru kullanıcı arayüzüne bağlayarak çalıştır
    app = BackgroundRemoverUI(ai_engine=ai_engine)
    app.mainloop()
