"""
Documentation translation module for AccuDoc.
Provides functionality to translate generated documentation into multiple languages.
"""

from typing import Dict, Optional
import re


class DocumentTranslator:
    """Translates documentation content into different languages."""
    
    # Supported languages for documentation translation
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch',
        'zh': '中文',
        'ja': '日本語',
        'ar': 'العربية',
    }
    
    def __init__(self, target_language: str = 'en'):
        """
        Initialize the document translator.
        
        Args:
            target_language: Target language code (e.g., 'es', 'fr')
        """
        self.target_language = target_language
        self._load_translations()
    
    def _load_translations(self):
        """Load translation dictionaries for documentation elements."""
        # Common documentation section headers and terms
        self.translations = {
            'en': {
                # Headers
                'overview': 'Overview',
                'features': 'Features',
                'technology_stack': 'Technology Stack',
                'installation': 'Installation',
                'usage': 'Usage',
                'project_structure': 'Project Structure',
                'license': 'License',
                'documentation': 'Documentation',
                'dependencies': 'Dependencies',
                'contributors': 'Contributors',
                'changelog': 'Changelog',
                'api_reference': 'API Reference',
                'configuration': 'Configuration',
                'getting_started': 'Getting Started',
                'prerequisites': 'Prerequisites',
                'examples': 'Examples',
                'testing': 'Testing',
                'deployment': 'Deployment',
                'troubleshooting': 'Troubleshooting',
                'contributing': 'Contributing',
                'code_of_conduct': 'Code of Conduct',
                'security': 'Security',
                'architecture': 'Architecture',
                
                # Common terms
                'required': 'Required',
                'optional': 'Optional',
                'version': 'Version',
                'author': 'Author',
                'description': 'Description',
                'name': 'Name',
                'type': 'Type',
                'default': 'Default',
                'example': 'Example',
                'note': 'Note',
                'warning': 'Warning',
                'important': 'Important',
                'tip': 'Tip',
                'see_also': 'See Also',
                'parameters': 'Parameters',
                'returns': 'Returns',
                'raises': 'Raises',
                'attributes': 'Attributes',
                'methods': 'Methods',
                'classes': 'Classes',
                'functions': 'Functions',
                'modules': 'Modules',
                'packages': 'Packages',
                
                # Instructions
                'step': 'Step',
                'run_command': 'Run the following command',
                'install_dependencies': 'Install dependencies',
                'clone_repository': 'Clone the repository',
                'navigate_to': 'Navigate to',
                'run_tests': 'Run tests',
                'build_project': 'Build the project',
                'start_server': 'Start the server',
            },
            'es': {
                # Headers
                'overview': 'Descripción General',
                'features': 'Características',
                'technology_stack': 'Stack Tecnológico',
                'installation': 'Instalación',
                'usage': 'Uso',
                'project_structure': 'Estructura del Proyecto',
                'license': 'Licencia',
                'documentation': 'Documentación',
                'dependencies': 'Dependencias',
                'contributors': 'Colaboradores',
                'changelog': 'Registro de Cambios',
                'api_reference': 'Referencia de API',
                'configuration': 'Configuración',
                'getting_started': 'Primeros Pasos',
                'prerequisites': 'Requisitos Previos',
                'examples': 'Ejemplos',
                'testing': 'Pruebas',
                'deployment': 'Despliegue',
                'troubleshooting': 'Solución de Problemas',
                'contributing': 'Contribuir',
                'code_of_conduct': 'Código de Conducta',
                'security': 'Seguridad',
                'architecture': 'Arquitectura',
                
                # Common terms
                'required': 'Requerido',
                'optional': 'Opcional',
                'version': 'Versión',
                'author': 'Autor',
                'description': 'Descripción',
                'name': 'Nombre',
                'type': 'Tipo',
                'default': 'Predeterminado',
                'example': 'Ejemplo',
                'note': 'Nota',
                'warning': 'Advertencia',
                'important': 'Importante',
                'tip': 'Consejo',
                'see_also': 'Ver También',
                'parameters': 'Parámetros',
                'returns': 'Devuelve',
                'raises': 'Lanza',
                'attributes': 'Atributos',
                'methods': 'Métodos',
                'classes': 'Clases',
                'functions': 'Funciones',
                'modules': 'Módulos',
                'packages': 'Paquetes',
                
                # Instructions
                'step': 'Paso',
                'run_command': 'Ejecuta el siguiente comando',
                'install_dependencies': 'Instalar dependencias',
                'clone_repository': 'Clonar el repositorio',
                'navigate_to': 'Navegar a',
                'run_tests': 'Ejecutar pruebas',
                'build_project': 'Compilar el proyecto',
                'start_server': 'Iniciar el servidor',
            },
            'fr': {
                # Headers
                'overview': 'Aperçu',
                'features': 'Fonctionnalités',
                'technology_stack': 'Stack Technologique',
                'installation': 'Installation',
                'usage': 'Utilisation',
                'project_structure': 'Structure du Projet',
                'license': 'Licence',
                'documentation': 'Documentation',
                'dependencies': 'Dépendances',
                'contributors': 'Contributeurs',
                'changelog': 'Journal des Modifications',
                'api_reference': 'Référence API',
                'configuration': 'Configuration',
                'getting_started': 'Démarrage',
                'prerequisites': 'Prérequis',
                'examples': 'Exemples',
                'testing': 'Tests',
                'deployment': 'Déploiement',
                'troubleshooting': 'Dépannage',
                'contributing': 'Contribuer',
                'code_of_conduct': 'Code de Conduite',
                'security': 'Sécurité',
                'architecture': 'Architecture',
                
                # Common terms
                'required': 'Requis',
                'optional': 'Optionnel',
                'version': 'Version',
                'author': 'Auteur',
                'description': 'Description',
                'name': 'Nom',
                'type': 'Type',
                'default': 'Par Défaut',
                'example': 'Exemple',
                'note': 'Note',
                'warning': 'Avertissement',
                'important': 'Important',
                'tip': 'Astuce',
                'see_also': 'Voir Aussi',
                'parameters': 'Paramètres',
                'returns': 'Retourne',
                'raises': 'Lève',
                'attributes': 'Attributs',
                'methods': 'Méthodes',
                'classes': 'Classes',
                'functions': 'Fonctions',
                'modules': 'Modules',
                'packages': 'Paquets',
                
                # Instructions
                'step': 'Étape',
                'run_command': 'Exécutez la commande suivante',
                'install_dependencies': 'Installer les dépendances',
                'clone_repository': 'Cloner le dépôt',
                'navigate_to': 'Naviguer vers',
                'run_tests': 'Exécuter les tests',
                'build_project': 'Compiler le projet',
                'start_server': 'Démarrer le serveur',
            },
            'de': {
                # Headers
                'overview': 'Übersicht',
                'features': 'Funktionen',
                'technology_stack': 'Technologie-Stack',
                'installation': 'Installation',
                'usage': 'Verwendung',
                'project_structure': 'Projektstruktur',
                'license': 'Lizenz',
                'documentation': 'Dokumentation',
                'dependencies': 'Abhängigkeiten',
                'contributors': 'Mitwirkende',
                'changelog': 'Änderungsprotokoll',
                'api_reference': 'API-Referenz',
                'configuration': 'Konfiguration',
                'getting_started': 'Erste Schritte',
                'prerequisites': 'Voraussetzungen',
                'examples': 'Beispiele',
                'testing': 'Tests',
                'deployment': 'Bereitstellung',
                'troubleshooting': 'Fehlerbehebung',
                'contributing': 'Mitwirken',
                'code_of_conduct': 'Verhaltenskodex',
                'security': 'Sicherheit',
                'architecture': 'Architektur',
                
                # Common terms
                'required': 'Erforderlich',
                'optional': 'Optional',
                'version': 'Version',
                'author': 'Autor',
                'description': 'Beschreibung',
                'name': 'Name',
                'type': 'Typ',
                'default': 'Standard',
                'example': 'Beispiel',
                'note': 'Hinweis',
                'warning': 'Warnung',
                'important': 'Wichtig',
                'tip': 'Tipp',
                'see_also': 'Siehe Auch',
                'parameters': 'Parameter',
                'returns': 'Gibt Zurück',
                'raises': 'Wirft',
                'attributes': 'Attribute',
                'methods': 'Methoden',
                'classes': 'Klassen',
                'functions': 'Funktionen',
                'modules': 'Module',
                'packages': 'Pakete',
                
                # Instructions
                'step': 'Schritt',
                'run_command': 'Führen Sie den folgenden Befehl aus',
                'install_dependencies': 'Abhängigkeiten installieren',
                'clone_repository': 'Repository klonen',
                'navigate_to': 'Navigieren zu',
                'run_tests': 'Tests ausführen',
                'build_project': 'Projekt erstellen',
                'start_server': 'Server starten',
            },
            'zh': {
                # Headers
                'overview': '概述',
                'features': '功能',
                'technology_stack': '技术栈',
                'installation': '安装',
                'usage': '使用',
                'project_structure': '项目结构',
                'license': '许可证',
                'documentation': '文档',
                'dependencies': '依赖项',
                'contributors': '贡献者',
                'changelog': '更新日志',
                'api_reference': 'API 参考',
                'configuration': '配置',
                'getting_started': '入门',
                'prerequisites': '先决条件',
                'examples': '示例',
                'testing': '测试',
                'deployment': '部署',
                'troubleshooting': '故障排除',
                'contributing': '贡献',
                'code_of_conduct': '行为准则',
                'security': '安全',
                'architecture': '架构',
                
                # Common terms
                'required': '必需',
                'optional': '可选',
                'version': '版本',
                'author': '作者',
                'description': '描述',
                'name': '名称',
                'type': '类型',
                'default': '默认',
                'example': '示例',
                'note': '注意',
                'warning': '警告',
                'important': '重要',
                'tip': '提示',
                'see_also': '另见',
                'parameters': '参数',
                'returns': '返回',
                'raises': '引发',
                'attributes': '属性',
                'methods': '方法',
                'classes': '类',
                'functions': '函数',
                'modules': '模块',
                'packages': '包',
                
                # Instructions
                'step': '步骤',
                'run_command': '运行以下命令',
                'install_dependencies': '安装依赖项',
                'clone_repository': '克隆仓库',
                'navigate_to': '导航到',
                'run_tests': '运行测试',
                'build_project': '构建项目',
                'start_server': '启动服务器',
            },
            'ja': {
                # Headers
                'overview': '概要',
                'features': '機能',
                'technology_stack': '技術スタック',
                'installation': 'インストール',
                'usage': '使用方法',
                'project_structure': 'プロジェクト構造',
                'license': 'ライセンス',
                'documentation': 'ドキュメント',
                'dependencies': '依存関係',
                'contributors': '貢献者',
                'changelog': '変更履歴',
                'api_reference': 'APIリファレンス',
                'configuration': '設定',
                'getting_started': 'はじめに',
                'prerequisites': '前提条件',
                'examples': '例',
                'testing': 'テスト',
                'deployment': 'デプロイメント',
                'troubleshooting': 'トラブルシューティング',
                'contributing': '貢献',
                'code_of_conduct': '行動規範',
                'security': 'セキュリティ',
                'architecture': 'アーキテクチャ',
                
                # Common terms
                'required': '必須',
                'optional': 'オプション',
                'version': 'バージョン',
                'author': '著者',
                'description': '説明',
                'name': '名前',
                'type': 'タイプ',
                'default': 'デフォルト',
                'example': '例',
                'note': '注意',
                'warning': '警告',
                'important': '重要',
                'tip': 'ヒント',
                'see_also': '関連項目',
                'parameters': 'パラメータ',
                'returns': '戻り値',
                'raises': '例外',
                'attributes': '属性',
                'methods': 'メソッド',
                'classes': 'クラス',
                'functions': '関数',
                'modules': 'モジュール',
                'packages': 'パッケージ',
                
                # Instructions
                'step': 'ステップ',
                'run_command': '次のコマンドを実行',
                'install_dependencies': '依存関係をインストール',
                'clone_repository': 'リポジトリをクローン',
                'navigate_to': '移動先',
                'run_tests': 'テストを実行',
                'build_project': 'プロジェクトをビルド',
                'start_server': 'サーバーを起動',
            },
            'ar': {
                # Headers
                'overview': 'نظرة عامة',
                'features': 'الميزات',
                'technology_stack': 'المكدس التقني',
                'installation': 'التثبيت',
                'usage': 'الاستخدام',
                'project_structure': 'هيكل المشروع',
                'license': 'الرخصة',
                'documentation': 'التوثيق',
                'dependencies': 'التبعيات',
                'contributors': 'المساهمون',
                'changelog': 'سجل التغييرات',
                'api_reference': 'مرجع API',
                'configuration': 'التكوين',
                'getting_started': 'البدء',
                'prerequisites': 'المتطلبات الأساسية',
                'examples': 'أمثلة',
                'testing': 'الاختبار',
                'deployment': 'النشر',
                'troubleshooting': 'استكشاف الأخطاء',
                'contributing': 'المساهمة',
                'code_of_conduct': 'قواعد السلوك',
                'security': 'الأمان',
                'architecture': 'البنية',
                
                # Common terms
                'required': 'مطلوب',
                'optional': 'اختياري',
                'version': 'الإصدار',
                'author': 'المؤلف',
                'description': 'الوصف',
                'name': 'الاسم',
                'type': 'النوع',
                'default': 'الافتراضي',
                'example': 'مثال',
                'note': 'ملاحظة',
                'warning': 'تحذير',
                'important': 'هام',
                'tip': 'نصيحة',
                'see_also': 'انظر أيضا',
                'parameters': 'المعاملات',
                'returns': 'يعيد',
                'raises': 'يثير',
                'attributes': 'السمات',
                'methods': 'الطرق',
                'classes': 'الفئات',
                'functions': 'الدوال',
                'modules': 'الوحدات',
                'packages': 'الحزم',
                
                # Instructions
                'step': 'خطوة',
                'run_command': 'قم بتشغيل الأمر التالي',
                'install_dependencies': 'تثبيت التبعيات',
                'clone_repository': 'استنساخ المستودع',
                'navigate_to': 'انتقل إلى',
                'run_tests': 'تشغيل الاختبارات',
                'build_project': 'بناء المشروع',
                'start_server': 'بدء الخادم',
            },
        }
    
    def translate(self, content: str) -> str:
        """
        Translate documentation content to the target language.
        
        Args:
            content: Original documentation content in English
            
        Returns:
            Translated documentation content
        """
        if self.target_language == 'en':
            # No translation needed for English
            return content
        
        translated = content
        
        # Get translations for target language
        target_trans = self.translations.get(self.target_language, {})
        source_trans = self.translations.get('en', {})
        
        # Translate section headers (markdown headers)
        for key, english_term in source_trans.items():
            if key in target_trans:
                translated_term = target_trans[key]
                
                # Replace in headers (## Header, ### Header, etc.)
                # Case-insensitive replacement for headers
                pattern = r'(#{1,6}\s+)' + re.escape(english_term) + r'(\s|$)'
                replacement = r'\1' + translated_term + r'\2'
                translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)
                
                # Replace standalone terms (with word boundaries)
                # This catches terms in bold, italic, or plain text
                pattern = r'\b' + re.escape(english_term) + r'\b'
                translated = re.sub(pattern, translated_term, translated)
        
        return translated
    
    def translate_with_note(self, content: str) -> str:
        """
        Translate documentation and add a translation note at the top.
        
        Args:
            content: Original documentation content
            
        Returns:
            Translated content with translation note
        """
        if self.target_language == 'en':
            return content
        
        # Translation note
        language_name = self.SUPPORTED_LANGUAGES.get(self.target_language, self.target_language)
        note_translations = {
            'es': f'> **Nota de Traducción**: Esta documentación ha sido traducida automáticamente al {language_name}. '
                  f'Algunos términos técnicos pueden mantenerse en inglés para mayor claridad.\n\n',
            'fr': f'> **Note de Traduction**: Cette documentation a été traduite automatiquement en {language_name}. '
                  f'Certains termes techniques peuvent rester en anglais pour plus de clarté.\n\n',
            'de': f'> **Übersetzungshinweis**: Diese Dokumentation wurde automatisch ins {language_name} übersetzt. '
                  f'Einige technische Begriffe können zur besseren Verständlichkeit auf Englisch bleiben.\n\n',
            'zh': f'> **翻译说明**：此文档已自动翻译为{language_name}。某些技术术语可能保留英文以确保清晰度。\n\n',
            'ja': f'> **翻訳ノート**：このドキュメントは自動的に{language_name}に翻訳されました。'
                  f'一部の技術用語は明確さのために英語のまま残されている場合があります。\n\n',
            'ar': f'> **ملاحظة الترجمة**: تمت ترجمة هذه الوثائق تلقائيًا إلى {language_name}. '
                  f'قد تبقى بعض المصطلحات التقنية باللغة الإنجليزية للوضوح.\n\n',
        }
        
        note = note_translations.get(self.target_language, '')
        translated_content = self.translate(content)
        
        return note + translated_content
    
    @staticmethod
    def get_supported_languages() -> Dict[str, str]:
        """
        Get all supported languages for documentation translation.
        
        Returns:
            Dictionary mapping language codes to language names
        """
        return DocumentTranslator.SUPPORTED_LANGUAGES.copy()
    
    @staticmethod
    def is_supported(language: str) -> bool:
        """
        Check if a language is supported for translation.
        
        Args:
            language: Language code
            
        Returns:
            True if language is supported
        """
        return language in DocumentTranslator.SUPPORTED_LANGUAGES
