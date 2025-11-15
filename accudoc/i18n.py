"""
Internationalization (i18n) module for AccuDoc.
Provides multi-language support for the UI and generated documentation.
"""

import json
import locale
import os
from pathlib import Path
from typing import Dict, Optional


class I18n:
    """Internationalization manager for AccuDoc."""
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch',
        'zh': '中文',
        'ja': '日本語',
        'ar': 'العربية',
    }
    
    # RTL (Right-to-Left) languages
    RTL_LANGUAGES = {'ar', 'he', 'fa', 'ur'}
    
    def __init__(self, language: Optional[str] = None):
        """
        Initialize the i18n manager.
        
        Args:
            language: Language code (e.g., 'en', 'es'). If None, auto-detect.
        """
        self.translations: Dict[str, Dict[str, str]] = {}
        self.current_language = language or self._detect_language()
        self._load_translations()
    
    def _detect_language(self) -> str:
        """
        Auto-detect system language from locale.
        
        Returns:
            Language code (e.g., 'en', 'es')
        """
        try:
            # Try to get system locale using getlocale() (preferred method)
            system_locale = locale.getlocale()[0]
            if system_locale:
                # Extract language code (first 2 chars)
                lang_code = system_locale[:2].lower()
                if lang_code in self.SUPPORTED_LANGUAGES:
                    return lang_code
        except Exception:
            pass
        
        # Default to English
        return 'en'
    
    def _load_translations(self):
        """Load translation files for all supported languages."""
        translations_dir = Path(__file__).parent / 'translations'
        
        # If translations directory doesn't exist, use built-in translations
        if not translations_dir.exists():
            self._load_builtin_translations()
            return
        
        # Load from JSON files
        for lang_code in self.SUPPORTED_LANGUAGES.keys():
            translation_file = translations_dir / f'{lang_code}.json'
            if translation_file.exists():
                with open(translation_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
            else:
                # Fall back to built-in translations
                self.translations[lang_code] = self._get_builtin_translation(lang_code)
    
    def _load_builtin_translations(self):
        """Load built-in translations (embedded in code)."""
        for lang_code in self.SUPPORTED_LANGUAGES.keys():
            self.translations[lang_code] = self._get_builtin_translation(lang_code)
    
    def _get_builtin_translation(self, lang_code: str) -> Dict[str, str]:
        """
        Get built-in translations for a language.
        
        Args:
            lang_code: Language code
            
        Returns:
            Dictionary of translations
        """
        # English (base language)
        if lang_code == 'en':
            return {
                # Application
                'app_title': 'AccuDoc - Repository Documentation Generator',
                'ready': 'Ready',
                'scanning': 'Scanning...',
                'error': 'Error',
                'success': 'Success',
                
                # Menu
                'file': 'File',
                'edit': 'Edit',
                'view': 'View',
                'help': 'Help',
                'new_window': 'New Window',
                'exit': 'Exit',
                'about': 'About',
                'settings': 'Settings',
                'preferences': 'Preferences',
                
                # Buttons
                'scan': 'Scan Repository',
                'save': 'Save Documentation',
                'browse': 'Browse Local...',
                'cancel': 'Cancel',
                'ok': 'OK',
                'apply': 'Apply',
                'close': 'Close',
                
                # Labels
                'repository': 'Repository URL or Local Path:',
                'template': 'Template:',
                'format': 'Format:',
                'language': 'Language:',
                'theme': 'Theme:',
                'output': 'Output:',
                'status': 'Status:',
                
                # Templates
                'template_default': 'Default',
                'template_minimal': 'Minimal',
                'template_detailed': 'Detailed',
                'template_api': 'API Reference',
                'template_readme': 'README Style',
                'template_student': 'Student Project',
                
                # Messages
                'select_directory': 'Select Repository Directory',
                'save_file': 'Save Documentation',
                'scanning_repository': 'Scanning repository...',
                'generating_docs': 'Generating documentation...',
                'scan_complete': 'Scan completed successfully!',
                'docs_saved': 'Documentation saved successfully!',
                'error_occurred': 'An error occurred: {error}',
                'no_repo': 'Please enter a repository URL or path.',
                
                # Settings
                'general': 'General',
                'appearance': 'Appearance',
                'language_setting': 'Language',
                'auto_detect': 'Auto-detect',
                'restart_required': 'Language change will take effect after restart.',
            }
        
        # Spanish
        elif lang_code == 'es':
            return {
                'app_title': 'AccuDoc - Generador de Documentación de Repositorios',
                'ready': 'Listo',
                'scanning': 'Escaneando...',
                'error': 'Error',
                'success': 'Éxito',
                
                'file': 'Archivo',
                'edit': 'Editar',
                'view': 'Ver',
                'help': 'Ayuda',
                'new_window': 'Nueva Ventana',
                'exit': 'Salir',
                'about': 'Acerca de',
                'settings': 'Configuración',
                'preferences': 'Preferencias',
                
                'scan': 'Escanear Repositorio',
                'save': 'Guardar Documentación',
                'browse': 'Explorar Local...',
                'cancel': 'Cancelar',
                'ok': 'Aceptar',
                'apply': 'Aplicar',
                'close': 'Cerrar',
                
                'repository': 'URL del Repositorio o Ruta Local:',
                'template': 'Plantilla:',
                'format': 'Formato:',
                'language': 'Idioma:',
                'theme': 'Tema:',
                'output': 'Salida:',
                'status': 'Estado:',
                
                'template_default': 'Predeterminado',
                'template_minimal': 'Mínimo',
                'template_detailed': 'Detallado',
                'template_api': 'Referencia API',
                'template_readme': 'Estilo README',
                'template_student': 'Proyecto Estudiantil',
                
                'select_directory': 'Seleccionar Directorio del Repositorio',
                'save_file': 'Guardar Documentación',
                'scanning_repository': 'Escaneando repositorio...',
                'generating_docs': 'Generando documentación...',
                'scan_complete': '¡Escaneo completado exitosamente!',
                'docs_saved': '¡Documentación guardada exitosamente!',
                'error_occurred': 'Ocurrió un error: {error}',
                'no_repo': 'Por favor ingrese una URL o ruta de repositorio.',
                
                'general': 'General',
                'appearance': 'Apariencia',
                'language_setting': 'Idioma',
                'auto_detect': 'Detectar automáticamente',
                'restart_required': 'El cambio de idioma tomará efecto después de reiniciar.',
            }
        
        # French
        elif lang_code == 'fr':
            return {
                'app_title': 'AccuDoc - Générateur de Documentation de Dépôt',
                'ready': 'Prêt',
                'scanning': 'Analyse en cours...',
                'error': 'Erreur',
                'success': 'Succès',
                
                'file': 'Fichier',
                'edit': 'Éditer',
                'view': 'Affichage',
                'help': 'Aide',
                'new_window': 'Nouvelle Fenêtre',
                'exit': 'Quitter',
                'about': 'À propos',
                'settings': 'Paramètres',
                'preferences': 'Préférences',
                
                'scan': 'Analyser le Dépôt',
                'save': 'Enregistrer la Documentation',
                'browse': 'Parcourir Local...',
                'cancel': 'Annuler',
                'ok': 'OK',
                'apply': 'Appliquer',
                'close': 'Fermer',
                
                'repository': 'URL du Dépôt ou Chemin Local:',
                'template': 'Modèle:',
                'format': 'Format:',
                'language': 'Langue:',
                'theme': 'Thème:',
                'output': 'Sortie:',
                'status': 'Statut:',
                
                'template_default': 'Par Défaut',
                'template_minimal': 'Minimal',
                'template_detailed': 'Détaillé',
                'template_api': 'Référence API',
                'template_readme': 'Style README',
                'template_student': 'Projet Étudiant',
                
                'select_directory': 'Sélectionner le Répertoire du Dépôt',
                'save_file': 'Enregistrer la Documentation',
                'scanning_repository': 'Analyse du dépôt...',
                'generating_docs': 'Génération de la documentation...',
                'scan_complete': 'Analyse terminée avec succès!',
                'docs_saved': 'Documentation enregistrée avec succès!',
                'error_occurred': 'Une erreur est survenue: {error}',
                'no_repo': 'Veuillez entrer une URL ou un chemin de dépôt.',
                
                'general': 'Général',
                'appearance': 'Apparence',
                'language_setting': 'Langue',
                'auto_detect': 'Détecter automatiquement',
                'restart_required': 'Le changement de langue prendra effet après le redémarrage.',
            }
        
        # German
        elif lang_code == 'de':
            return {
                'app_title': 'AccuDoc - Repository-Dokumentationsgenerator',
                'ready': 'Bereit',
                'scanning': 'Scannen...',
                'error': 'Fehler',
                'success': 'Erfolg',
                
                'file': 'Datei',
                'edit': 'Bearbeiten',
                'view': 'Ansicht',
                'help': 'Hilfe',
                'new_window': 'Neues Fenster',
                'exit': 'Beenden',
                'about': 'Über',
                'settings': 'Einstellungen',
                'preferences': 'Einstellungen',
                
                'scan': 'Repository Scannen',
                'save': 'Dokumentation Speichern',
                'browse': 'Lokal Durchsuchen...',
                'cancel': 'Abbrechen',
                'ok': 'OK',
                'apply': 'Anwenden',
                'close': 'Schließen',
                
                'repository': 'Repository-URL oder Lokaler Pfad:',
                'template': 'Vorlage:',
                'format': 'Format:',
                'language': 'Sprache:',
                'theme': 'Design:',
                'output': 'Ausgabe:',
                'status': 'Status:',
                
                'template_default': 'Standard',
                'template_minimal': 'Minimal',
                'template_detailed': 'Detailliert',
                'template_api': 'API-Referenz',
                'template_readme': 'README-Stil',
                'template_student': 'Studentenprojekt',
                
                'select_directory': 'Repository-Verzeichnis Auswählen',
                'save_file': 'Dokumentation Speichern',
                'scanning_repository': 'Repository wird gescannt...',
                'generating_docs': 'Dokumentation wird generiert...',
                'scan_complete': 'Scannen erfolgreich abgeschlossen!',
                'docs_saved': 'Dokumentation erfolgreich gespeichert!',
                'error_occurred': 'Ein Fehler ist aufgetreten: {error}',
                'no_repo': 'Bitte geben Sie eine Repository-URL oder einen Pfad ein.',
                
                'general': 'Allgemein',
                'appearance': 'Erscheinungsbild',
                'language_setting': 'Sprache',
                'auto_detect': 'Automatisch erkennen',
                'restart_required': 'Die Sprachänderung wird nach dem Neustart wirksam.',
            }
        
        # Chinese
        elif lang_code == 'zh':
            return {
                'app_title': 'AccuDoc - 仓库文档生成器',
                'ready': '就绪',
                'scanning': '扫描中...',
                'error': '错误',
                'success': '成功',
                
                'file': '文件',
                'edit': '编辑',
                'view': '查看',
                'help': '帮助',
                'new_window': '新窗口',
                'exit': '退出',
                'about': '关于',
                'settings': '设置',
                'preferences': '首选项',
                
                'scan': '扫描仓库',
                'save': '保存文档',
                'browse': '浏览本地...',
                'cancel': '取消',
                'ok': '确定',
                'apply': '应用',
                'close': '关闭',
                
                'repository': '仓库 URL 或本地路径:',
                'template': '模板:',
                'format': '格式:',
                'language': '语言:',
                'theme': '主题:',
                'output': '输出:',
                'status': '状态:',
                
                'template_default': '默认',
                'template_minimal': '最小',
                'template_detailed': '详细',
                'template_api': 'API 参考',
                'template_readme': 'README 样式',
                'template_student': '学生项目',
                
                'select_directory': '选择仓库目录',
                'save_file': '保存文档',
                'scanning_repository': '正在扫描仓库...',
                'generating_docs': '正在生成文档...',
                'scan_complete': '扫描成功完成！',
                'docs_saved': '文档保存成功！',
                'error_occurred': '发生错误: {error}',
                'no_repo': '请输入仓库 URL 或路径。',
                
                'general': '常规',
                'appearance': '外观',
                'language_setting': '语言',
                'auto_detect': '自动检测',
                'restart_required': '语言更改将在重启后生效。',
            }
        
        # Japanese
        elif lang_code == 'ja':
            return {
                'app_title': 'AccuDoc - リポジトリドキュメント生成ツール',
                'ready': '準備完了',
                'scanning': 'スキャン中...',
                'error': 'エラー',
                'success': '成功',
                
                'file': 'ファイル',
                'edit': '編集',
                'view': '表示',
                'help': 'ヘルプ',
                'new_window': '新しいウィンドウ',
                'exit': '終了',
                'about': 'について',
                'settings': '設定',
                'preferences': '環境設定',
                
                'scan': 'リポジトリをスキャン',
                'save': 'ドキュメントを保存',
                'browse': 'ローカルを参照...',
                'cancel': 'キャンセル',
                'ok': 'OK',
                'apply': '適用',
                'close': '閉じる',
                
                'repository': 'リポジトリ URL またはローカルパス:',
                'template': 'テンプレート:',
                'format': 'フォーマット:',
                'language': '言語:',
                'theme': 'テーマ:',
                'output': '出力:',
                'status': 'ステータス:',
                
                'template_default': 'デフォルト',
                'template_minimal': 'ミニマル',
                'template_detailed': '詳細',
                'template_api': 'APIリファレンス',
                'template_readme': 'READMEスタイル',
                'template_student': '学生プロジェクト',
                
                'select_directory': 'リポジトリディレクトリを選択',
                'save_file': 'ドキュメントを保存',
                'scanning_repository': 'リポジトリをスキャン中...',
                'generating_docs': 'ドキュメントを生成中...',
                'scan_complete': 'スキャンが正常に完了しました！',
                'docs_saved': 'ドキュメントが正常に保存されました！',
                'error_occurred': 'エラーが発生しました: {error}',
                'no_repo': 'リポジトリの URL またはパスを入力してください。',
                
                'general': '一般',
                'appearance': '外観',
                'language_setting': '言語',
                'auto_detect': '自動検出',
                'restart_required': '言語の変更は再起動後に有効になります。',
            }
        
        # Arabic (RTL)
        elif lang_code == 'ar':
            return {
                'app_title': 'AccuDoc - مولد توثيق المستودعات',
                'ready': 'جاهز',
                'scanning': 'جارٍ المسح...',
                'error': 'خطأ',
                'success': 'نجح',
                
                'file': 'ملف',
                'edit': 'تحرير',
                'view': 'عرض',
                'help': 'مساعدة',
                'new_window': 'نافذة جديدة',
                'exit': 'خروج',
                'about': 'حول',
                'settings': 'إعدادات',
                'preferences': 'تفضيلات',
                
                'scan': 'مسح المستودع',
                'save': 'حفظ التوثيق',
                'browse': 'تصفح محلي...',
                'cancel': 'إلغاء',
                'ok': 'موافق',
                'apply': 'تطبيق',
                'close': 'إغلاق',
                
                'repository': 'رابط المستودع أو المسار المحلي:',
                'template': 'قالب:',
                'format': 'التنسيق:',
                'language': 'اللغة:',
                'theme': 'السمة:',
                'output': 'الإخراج:',
                'status': 'الحالة:',
                
                'template_default': 'افتراضي',
                'template_minimal': 'الحد الأدنى',
                'template_detailed': 'مفصل',
                'template_api': 'مرجع API',
                'template_readme': 'نمط README',
                'template_student': 'مشروع الطالب',
                
                'select_directory': 'حدد دليل المستودع',
                'save_file': 'حفظ التوثيق',
                'scanning_repository': 'جارٍ مسح المستودع...',
                'generating_docs': 'جارٍ إنشاء التوثيق...',
                'scan_complete': 'اكتمل المسح بنجاح!',
                'docs_saved': 'تم حفظ التوثيق بنجاح!',
                'error_occurred': 'حدث خطأ: {error}',
                'no_repo': 'الرجاء إدخال رابط أو مسار المستودع.',
                
                'general': 'عام',
                'appearance': 'المظهر',
                'language_setting': 'اللغة',
                'auto_detect': 'اكتشاف تلقائي',
                'restart_required': 'سيتم تطبيق تغيير اللغة بعد إعادة التشغيل.',
            }
        
        # Default to English for any other language
        else:
            return self._get_builtin_translation('en')
    
    def get(self, key: str, **kwargs) -> str:
        """
        Get translated string for the current language.
        
        Args:
            key: Translation key
            **kwargs: Format parameters for the string
            
        Returns:
            Translated string
        """
        # Get translation from current language, fall back to English
        translation = self.translations.get(self.current_language, {}).get(key)
        if translation is None:
            translation = self.translations.get('en', {}).get(key, key)
        
        # Format with parameters if provided
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        return translation
    
    def set_language(self, language: str):
        """
        Change the current language.
        
        Args:
            language: Language code (e.g., 'en', 'es')
        """
        if language in self.SUPPORTED_LANGUAGES:
            self.current_language = language
    
    def get_language(self) -> str:
        """Get the current language code."""
        return self.current_language
    
    def is_rtl(self) -> bool:
        """
        Check if current language is right-to-left.
        
        Returns:
            True if current language is RTL
        """
        return self.current_language in self.RTL_LANGUAGES
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get all supported languages.
        
        Returns:
            Dictionary mapping language codes to names
        """
        return self.SUPPORTED_LANGUAGES.copy()


# Global i18n instance
_i18n_instance: Optional[I18n] = None


def get_i18n(language: Optional[str] = None) -> I18n:
    """
    Get the global i18n instance.
    
    Args:
        language: Language code. If None, use existing or auto-detect.
        
    Returns:
        I18n instance
    """
    global _i18n_instance
    if _i18n_instance is None or language is not None:
        _i18n_instance = I18n(language)
    return _i18n_instance


def _(key: str, **kwargs) -> str:
    """
    Shorthand function for translation.
    
    Args:
        key: Translation key
        **kwargs: Format parameters
        
    Returns:
        Translated string
    """
    return get_i18n().get(key, **kwargs)
