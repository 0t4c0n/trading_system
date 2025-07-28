# 📈 Conservative Trading Bot

> **Análisis semanal automatizado de acciones para inversión conservadora a largo plazo**

[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Enabled-brightgreen)](../../actions)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-yellow.svg)](https://python.org)

## 🎯 **¿Qué hace este bot?**

Este bot automatiza el análisis semanal de **más de 3,000 acciones** del NYSE y NASDAQ para identificar las mejores oportunidades de inversión conservadora con **holds de 2-3 meses**.

### **Filosofía de inversión:**
- 🎯 **Objetivo:** Superar al SPY (S&P 500) con riesgo controlado
- ⏰ **Horizonte:** 2-3 meses por posición (NO day trading)
- 🔍 **Método:** Análisis de consistencia semanal + filtros técnicos/fundamentales
- 📊 **Decisiones:** Basadas en patrones, no en ruido del mercado

---

## ✨ **Características principales**

### **🔄 Automático cada lunes**
- Screening de 3,000+ acciones NYSE + NASDAQ
- Análisis de consistencia (últimas 5 semanas)
- Recomendaciones de rotación de cartera
- Dashboard web actualizado automáticamente

### **🏆 Sistema de consistencia**
- **Consistent Winners:** Aparecen 4+ semanas → Alta confianza
- **Strong Candidates:** Aparecen 3 semanas → Buena confianza  
- **Emerging Opportunities:** Aparecen 2 semanas → Vigilar
- **Newly Emerged:** Primera aparición → Esperar confirmación

### **🎯 Filtros estrictos**
**Técnicos:**
- Tendencia sólida: MA21 > MA50 > MA200
- Outperformance vs SPY en múltiples plazos (20d, 60d, 90d)
- Stop-loss calculado ≤ 15% riesgo
- Volumen mínimo 1M acciones

**Fundamentales:**
- Beneficios positivos último trimestre
- Crecimiento de beneficios > 15% o ingresos > 10%
- ROE > 15% (cuando disponible)

---

## 🚀 **Setup rápido (5 minutos)**

### **1. Fork este repositorio**
```bash
# Click en "Fork" arriba a la derecha
# O crea un nuevo repo y copia los archivos
```

### **2. Habilitar GitHub Actions**
- Ve a **Settings** > **Actions** > **General**
- Selecciona **"Allow all actions"**
- En **Workflow permissions**: **"Read and write permissions"**

### **3. Configurar GitHub Pages**
- Ve a **Settings** > **Pages**
- Source: **"GitHub Actions"**

### **4. Configurar tu cartera**
Edita `current_portfolio.json` con tus posiciones reales:

```json
{
  "positions": {
    "AAPL": {
      "shares": 100,
      "entry_price": 150.25,
      "entry_date": "2024-01-15T14:30:00Z",
      "broker": "Interactive Brokers"
    }
  },
  "cash": 5000.00,
  "last_manual_update": "2024-01-29T10:00:00Z"
}
```

### **5. Primera ejecución**
- Ve a **Actions** > **"Weekly Conservative Stock Analysis"**
- Click **"Run workflow"**
- Espera 10-15 minutos

### **6. ¡Ya está!**
Tu dashboard estará en: `https://TU_USUARIO.github.io/NOMBRE_REPO/`

---

## 📊 **Ejemplo de dashboard**

![Dashboard Preview](https://via.placeholder.com/500x300/27ae60/ffffff?text=Conservative+Trading+Bot+Dashboard)

**Dashboard incluye:**
- 📈 Resumen ejecutivo semanal
- 🏆 Consistent winners y strong candidates
- 🔄 Recomendaciones de rotación específicas
- 📊 Contexto de mercado (SPY performance)
- 🎯 Acciones requeridas claras

---

## 🔄 **Workflow semanal**

### **Automático (Lunes 3 PM España):**
1. ✅ Screening completo 3,000+ acciones
2. ✅ Análisis de consistencia vs historial
3. ✅ Generación de recomendaciones
4. ✅ Actualización de dashboard
5. ✅ Commit automático con resultados

### **Manual (cuando quieras):**
1. 👀 Revisar dashboard y reporte semanal
2. 🤔 Evaluar recomendaciones de "Acción requerida"
3. 💰 Ejecutar trades en tu broker (opcional)
4. ✏️ Actualizar `current_portfolio.json` con cambios reales

---

## 📁 **Estructura del proyecto**

```
conservative-trading-bot/
├── README.md                          # Este archivo
├── GUÍA_DE_IMPLEMENTACIÓN_COMPLETA.md # Guía paso a paso
├── requirements.txt                    # Dependencias Python
├── current_portfolio.json             # TU cartera (editar)
│
├── 🔍 Scripts de análisis:
├── conservative_screener.py           # Screening principal
├── consistency_analyzer.py            # Análisis de consistencia
├── rotation_recommender.py            # Recomendaciones
├── create_weekly_report.py            # Generador de reportes
│
├── 🤖 Automatización:
├── .github/workflows/
│   └── weekly_conservative_analysis.yml # GitHub Actions
│
├── 🌐 Dashboard:
└── docs/
    ├── index.html                      # Dashboard web
    └── data.json                       # Datos (generado automáticamente)
```

---

## 📈 **Resultados esperados**

### **Rendimiento objetivo:**
- 🎯 **Superar SPY** en periodos de 6-12 meses
- 📉 **Drawdown máximo:** <20% (vs SPY ~25%)
- 🔄 **Rotaciones:** 4-8 por año (baja frecuencia)

### **Características de las recomendaciones:**
- 🏆 **Consistencia:** Solo acciones que aparecen 3+ semanas
- 🛡️ **Riesgo controlado:** Stop-loss automático ≤15%
- 📊 **Outperformance:** Superan SPY en múltiples plazos
- 💪 **Fundamentales sólidos:** Beneficios y crecimiento positivos

---

## 🛠️ **Personalización**

### **Ajustar filtros (conservative_screener.py):**
```python
# Cambiar umbrales de outperformance
outperformance_60d > 5  # Cambiar a 3 para menos estricto

# Ajustar riesgo máximo
if risk_pct > 15:  # Cambiar a 10 para más conservador

# Modificar volumen mínimo
if volume_avg_30d < 1_000_000:  # 500K para incluir más acciones
```

### **Cambiar frecuencia (workflow YAML):**
```yaml
schedule:
  - cron: '0 14 * * 1'    # Lunes (actual)
  - cron: '0 14 * * 1,4'  # Lunes y jueves
```

---

## 🔧 **Troubleshooting común**

### **❌ Workflow falla**
- Verificar permisos en Settings > Actions
- Rate limiting: Esperar y volver a ejecutar
- Revisar logs específicos en Actions

### **🌐 Dashboard no carga**
- Verificar GitHub Pages habilitado
- Esperar 5-10 minutos para propagación
- Verificar que `docs/data.json` existe

### **📊 Sin datos en dashboard**
- Ejecutar workflow manualmente una vez
- Verificar que todos los scripts terminaron OK
- Revisar logs de `create_weekly_report.py`

**[Ver guía completa de troubleshooting](GUÍA_DE_IMPLEMENTACIÓN_COMPLETA.md#troubleshooting)**

---

## 🤝 **Contribuciones**

¿Tienes ideas para mejorar el bot? ¡Genial!

1. 🍴 Fork el proyecto
2. 🌟 Crea una branch para tu feature (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push a la branch (`git push origin feature/AmazingFeature`)
5. 🔄 Abre un Pull Request

### **Ideas para contribuir:**
- 📊 Nuevos indicadores técnicos
- 🌍 Soporte para mercados internacionales
- 📱 Notificaciones móviles
- 📈 Backtesting histórico
- 🎨 Mejoras al dashboard

---

## ⚖️ **Disclaimer**

> **⚠️ IMPORTANTE:** Este bot es para fines educativos e informativos únicamente. 
> 
> - 📊 **No es asesoramiento financiero**
> - 💰 **Invierte solo lo que puedas permitirte perder**
> - 🧠 **Haz tu propia investigación antes de invertir**
> - 📈 **Los rendimientos pasados no garantizan resultados futuros**
> - 🎯 **El creador no se responsabiliza por pérdidas**

---

## 📝 **Changelog**

### **v1.0.0** (Enero 2024)
- ✨ Lanzamiento inicial
- 🔍 Screening conservador con 8 filtros
- 📊 Análisis de consistencia semanal
- 🤖 Automatización completa con GitHub Actions
- 🌐 Dashboard web responsive
- 📋 Reportes semanales en Markdown

---

## 📞 **Soporte**

### **Documentación:**
- 📖 [Guía de implementación completa](GUÍA_DE_IMPLEMENTACIÓN_COMPLETA.md)
- 💡 [Ejemplos de uso](GUÍA_DE_IMPLEMENTACIÓN_COMPLETA.md#ejemplos-de-uso)
- 🛠️ [Troubleshooting](GUÍA_DE_IMPLEMENTACIÓN_COMPLETA.md#troubleshooting)

### **Contacto:**
- 🐛 **Issues:** [GitHub Issues](../../issues)
- 💬 **Discusiones:** [GitHub Discussions](../../discussions)
- 📧 **Email:** [Crear un issue](../../issues/new)

---

## 📄 **Licencia**

Este proyecto está bajo la licencia MIT - ver [LICENSE](LICENSE) para detalles.

---

## 🌟 **¿Te gusta el proyecto?**

Si este bot te resulta útil:

- ⭐ **Dale una estrella** a este repositorio
- 🍴 **Compártelo** con otros inversores
- 🔄 **Fork** y personalízalo para tus necesidades
- 💡 **Contribuye** con mejoras

---

<div align="center">

**🚀 Desarrollado por [0t4c0n](https://github.com/0t4c0n)**

*"La consistencia supera a la perfección en inversión"*

</div>