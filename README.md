# 📈 Conservative Trading Bot - Monthly Trading Edition

> **Análisis diario automatizado de acciones para trades mensuales con gestión conservadora**

[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Daily-brightgreen)](../../actions)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-yellow.svg)](https://python.org)
[![MA50 Bonus](https://img.shields.io/badge/MA50%20Bonus-+22pts-gold.svg)](conservative_screener.py)

## 🎯 **¿Qué hace este bot?**

Este bot automatiza el análisis **diario** de **más de 3,000 acciones** del NYSE y NASDAQ para identificar las mejores oportunidades de **trading mensual** (~1 mes por posición) con gestión conservadora de riesgos.

### **🔄 Nueva Filosofía: "Daily Monitoring, Monthly Trading"**
- 🎯 **Objetivo:** Trades de ~1 mes con monitorización diaria  
- ⏰ **Ejecución:** Diaria (Lunes-Viernes 15:30 España)
- 🔍 **Rotaciones:** Solo con criterios estrictos (+30 puntos, stop loss cercano, momentum perdido)
- 🌟 **Bonus MA50:** +22 puntos por rebotes alcistas en MA50

---

## ✨ **Características principales**

### **🔄 Automático cada día de trading**
- **Lunes a Viernes 15:30 España** (post-market USA)
- Screening de 3,000+ acciones NYSE + NASDAQ
- Análisis de consistencia (últimos 7 días)
- Recomendaciones de rotación **solo cuando es crítico**
- Dashboard web actualizado automáticamente

### **🌟 Sistema MA50 Bonus (+22 puntos)**
- **Rebotes en MA50:** +22 puntos de score por señal alcista
- **Prioridad MA50:** Stop loss en MA50 prioritario sobre otros métodos
- **Multiplicador 20%:** Bonus adicional del 20% en score final
- **Detección automática:** Sistema identifica rebotes técnicos

### **🎯 Criterios estrictos de rotación mensual**
**Solo recomienda cambios cuando:**
- 🚨 **Posición cerca del stop loss** (2-3% del stop)
- 📉 **Pérdida de momentum** (3+ días sin aparecer en screening)
- 🚀 **Oportunidad superior** (30+ puntos mejor que posición actual)
- 📊 **Deterioro fundamental** de posiciones actuales

### **🏆 Sistema de consistencia diario**
- **Consistent Winners:** Aparecen 4+ días → Alta confianza
- **Strong Candidates:** Aparecen 3 días → Buena confianza  
- **Emerging Opportunities:** Aparecen 2 días → Vigilar
- **Newly Emerged:** Primera aparición → Esperar confirmación

### **🛡️ Filtros ultra conservadores**
**Técnicos:**
- Tendencia sólida: MA21 > MA50 > MA200
- Outperformance vs SPY en múltiples plazos (20d, 60d)
- Stop-loss calculado ≤ 10% riesgo (SAGRADO)
- Volumen mínimo 1M acciones
- **Bonus MA50:** Prioridad máxima para rebotes

**Fundamentales:**
- Beneficios positivos último trimestre (OBLIGATORIO)
- Datos fundamentales completos requeridos
- Filtros estrictos de calidad

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

### **4. Configurar tu cartera para trading mensual**
Edita `current_portfolio.json` con tus posiciones reales:

```json
{
  "last_manual_update": "2025-01-29T10:00:00Z",
  "positions": {
    "AAPL": {
      "shares": 100,
      "entry_price": 150.25,
      "entry_date": "2024-01-15T14:30:00Z",
      "broker": "Interactive Brokers",
      "notes": "Entrada tras breakout",
      "target_hold_period": "1_month"
    }
  },
  "cash": 5000.00,
  "strategy": {
    "max_positions": 5,
    "target_hold_period": "1 month with daily monitoring",
    "risk_per_position": "10% máximo",
    "rotation_philosophy": "Monthly trades with strict rotation criteria"
  }
}
```

### **5. Primera ejecución**
- Ve a **Actions** > **"Daily Conservative Stock Analysis"**
- Click **"Run workflow"**
- Espera 10-15 minutos

### **6. ¡Ya está!**
Tu dashboard estará en: `https://TU_USUARIO.github.io/NOMBRE_REPO/`

---

## 📊 **Dashboard optimizado para trading mensual**

**Dashboard incluye:**
- 📈 Resumen ejecutivo diario con perspectiva mensual
- 🌟 Acciones con bonus MA50 destacadas
- 🏆 Consistent winners y strong candidates (últimos 7 días)
- 🔄 Recomendaciones de rotación **solo críticas**
- 📊 Contexto de mercado (SPY performance)
- 🎯 Acciones requeridas **estrictamente filtradas**
- ⚠️ Alertas de stop loss y momentum perdido

---

## 🔄 **Workflow diario optimizado**

### **🤖 Automático (Lunes-Viernes 15:30 España):**
1. ✅ Screening completo 3,000+ acciones con **bonus MA50**
2. ✅ Análisis de consistencia últimos 7 días
3. ✅ Generación de recomendaciones **con criterios estrictos**
4. ✅ Actualización de dashboard diario
5. ✅ Commit automático con resultados

### **📋 Manual (cuando quieras):**
1. 👀 Revisar dashboard diario y alertas
2. 🤔 Evaluar recomendaciones **solo críticas**
3. 💰 Ejecutar trades en tu broker (si hay alertas urgentes)
4. ✏️ Actualizar `current_portfolio.json` con cambios reales
5. 📈 Mantener perspectiva mensual en decisiones

---

## 📁 **Estructura del proyecto**

```
conservative-trading-bot/
├── README.md                          # Este archivo (actualizado)
├── GUÍA_DE_IMPLEMENTACIÓN_COMPLETA.md # Guía paso a paso
├── requirements.txt                    # Dependencias Python
├── current_portfolio.json             # TU cartera (configurar para trading mensual)
│
├── 🔍 Scripts de análisis diario:
├── conservative_screener.py           # Screening con bonus MA50 (+22pts)
├── consistency_analyzer.py            # Análisis de consistencia últimos 7 días
├── rotation_recommender.py            # Recomendaciones con criterios estrictos
├── create_weekly_report.py            # Generador de reportes diarios
│
├── 🤖 Automatización diaria:
├── .github/workflows/
│   └── daily_conservative_analysis.yml # GitHub Actions (Lun-Vie 15:30)
│
├── 🌐 Dashboard:
└── docs/
    ├── index.html                      # Dashboard web (actualizado diario)
    └── data.json                       # Datos (generado automáticamente)
```

---

## 📈 **Resultados esperados con trading mensual**

### **Rendimiento objetivo actualizado:**
- 🎯 **Superar SPY** en periodos de 3-6 meses
- 📉 **Drawdown máximo:** <15% (vs SPY ~25%)
- 🔄 **Rotaciones:** 2-4 por mes (frecuencia controlada)
- 🌟 **Bonus MA50:** Identificar 20-30% más rebotes alcistas

### **Características de las recomendaciones mejoradas:**
- 🏆 **Consistencia:** Solo acciones que aparecen 3+ días consecutivos
- 🛡️ **Riesgo ultra controlado:** Stop-loss automático ≤10%
- 📊 **Outperformance:** Superan SPY en múltiples plazos
- 💪 **Fundamentales sólidos:** Beneficios positivos OBLIGATORIOS
- 🌟 **Señales técnicas:** Bonus MA50 para rebotes alcistas
- ⚠️ **Rotaciones selectivas:** Solo cuando criterios estrictos se cumplen

---

## 🛠️ **Personalización avanzada**

### **Ajustar bonus MA50 (conservative_screener.py):**
```python
# Cambiar bonus por rebote MA50
self.ma50_stop_bonus = 22  # Cambiar a 15 o 30 según preferencia

# Ajustar multiplicador de score
self.ma50_bonus_multiplier = 1.20  # 20% extra, cambiar a 1.15 o 1.25
```

### **Modificar criterios de rotación (rotation_recommender.py):**
```python
# Cambiar diferencia mínima de score para rotación
self.min_score_difference = 30.0  # Cambiar a 20 para más rotaciones o 40 para menos

# Ajustar proximidad al stop loss
self.stop_loss_proximity_threshold = 0.03  # 3%, cambiar a 0.02 para más sensibilidad

# Modificar días de momentum perdido
self.momentum_loss_days = 3  # Cambiar a 2 para más sensibilidad o 5 para menos
```

### **Cambiar frecuencia de ejecución (workflow YAML):**
```yaml
schedule:
  # Actual: Lunes-Viernes 15:30 España
  - cron: '30 14 * * 1-5'    
  
  # Solo 3 días por semana (Lun/Mie/Vie)
  - cron: '30 14 * * 1,3,5'  
  
  # Dos veces al día (mañana y tarde)
  - cron: '30 8,14 * * 1-5'
```

---

## 🌟 **Novedades en esta versión**

### **🔄 Ejecución diaria optimizada:**
- **Frecuencia:** Lunes-Viernes post-market
- **Filosofía:** Daily monitoring, monthly trading
- **Eficiencia:** Sin over-trading, rotaciones selectivas

### **🌟 Sistema MA50 Bonus:**
- **Detección automática:** Rebotes en MA50
- **Bonus significativo:** +22 puntos absolutos
- **Multiplicador:** 20% extra en score final
- **Prioridad técnica:** MA50 stop loss prioritario

### **⚠️ Criterios estrictos de rotación:**
- **Score difference:** Mínimo +30 puntos
- **Stop loss proximity:** Alerta a 3% del stop
- **Momentum loss:** 3+ días sin aparecer
- **High conviction:** Solo oportunidades excepcionales

### **📊 Gestión de riesgo mejorada:**
- **Risk cap:** Máximo 10% por posición (SAGRADO)
- **Quality filters:** Fundamentales positivos obligatorios
- **Technical signals:** Tendencia alcista confirmada
- **MA50 priority:** Sistema de stop loss mejorado

---

## 🔧 **Troubleshooting común**

### **❌ Workflow falla en ejecución diaria**
- Verificar permisos en Settings > Actions
- Rate limiting: Los mercados están cerrados los fines de semana
- Revisar logs específicos en Actions tab
- Verificar que el horario de ejecución sea post-market

### **🌟 Bonus MA50 no se aplica**
- Verificar que las acciones tengan datos de MA50 suficientes
- Confirmar que precio actual > MA50 * 0.985
- Revisar logs del screener para mensajes de bonus aplicado

### **🔄 Demasiadas/pocas recomendaciones**
- Ajustar `min_score_difference` en rotation_recommender.py
- Modificar `stop_loss_proximity_threshold` para sensibilidad
- Cambiar `momentum_loss_days` según preferencias

### **🌐 Dashboard no refleja cambios diarios**
- Verificar GitHub Pages habilitado
- Esperar 5-10 minutos para propagación
- Verificar que `docs/data.json` se actualiza diariamente

### **📊 Sin datos en dashboard**
- Ejecutar workflow manualmente una vez
- Verificar que todos los scripts terminaron OK en Actions
- Revisar logs de `create_weekly_report.py`

---

## 📈 **Ejemplos de uso para trading mensual**

### **🌟 Escenario 1: Nueva oportunidad con MA50 bonus**
```
📅 Día 1: NVDA aparece en screening con rebote MA50 (+22pts bonus)
📅 Día 2: NVDA mantiene consistencia, score sube a 95pts
📅 Día 3: Sistema recomienda NVDA (alta convicción, 3 días consecutivos)
💰 Acción: Considerar entrada para hold mensual
```

### **🌟 Escenario 2: Gestión de posición existente**
```
📅 Día 1-10: AAPL en portfolio, performance positiva
📅 Día 11: AAPL cerca de stop loss (2% restante)
🚨 Alerta: Sistema recomienda "CONSIDER_EXIT"
💰 Acción: Evaluar salida o ajustar stop loss
```

### **🌟 Escenario 3: Rotación selectiva**
```
📅 Posición actual: MSFT (score 65pts)
📅 Nueva oportunidad: GOOGL (score 98pts, +33pts diferencia)
✅ Criterio cumplido: +30pts mínimo
💰 Acción: Sistema recomienda rotación MSFT → GOOGL
```

---

## 🤝 **Contribuciones**

¿Tienes ideas para mejorar el bot? ¡Genial!

1. 🍴 Fork el proyecto
2. 🌟 Crea una branch para tu feature (`git checkout -b feature/MA50Enhancement`)
3. 💾 Commit tus cambios (`git commit -m 'Add MA50 bonus refinement'`)
4. 📤 Push a la branch (`git push origin feature/MA50Enhancement`)
5. 🔄 Abre un Pull Request

### **Ideas para contribuir:**
- 📊 Nuevos sistemas de bonus técnicos (MA200, RSI, etc.)
- 🌍 Soporte para mercados internacionales
- 📱 Notificaciones móviles para alertas críticas
- 📈 Backtesting histórico del sistema MA50
- 🎨 Mejoras al dashboard para trading mensual

---

## ⚖️ **Disclaimer**

> **⚠️ IMPORTANTE:** Este bot es para fines educativos e informativos únicamente. 
> 
> - 📊 **No es asesoramiento financiero**
> - 💰 **Invierte solo lo que puedas permitirte perder**
> - 🧠 **Haz tu propia investigación antes de invertir**
> - 📈 **Los rendimientos pasados no garantizan resultados futuros**
> - 🎯 **El creador no se responsabiliza por pérdidas**
> - 🌟 **El sistema MA50 bonus es experimental**

---

## 📝 **Changelog**

### **v2.0.0** (Febrero 2025) - Monthly Trading Edition
- 🔄 **Ejecución diaria:** Lun-Vie 15:30 España post-market
- 🌟 **Sistema MA50 Bonus:** +22 puntos por rebotes alcistas
- ⚠️ **Criterios estrictos:** Rotaciones solo con alta convicción
- 📊 **Filosofía mensual:** Daily monitoring, monthly trading
- 🛡️ **Risk management:** Stop loss ≤10% SAGRADO
- 📈 **Dashboard optimizado:** Vista diaria con perspectiva mensual

### **v1.0.0** (Enero 2024)
- ✨ Lanzamiento inicial semanal
- 🔍 Screening conservador con 8 filtros
- 📊 Análisis de consistencia semanal
- 🤖 Automatización con GitHub Actions
- 🌐 Dashboard web responsive

---

## 📞 **Soporte**

### **Documentación:**
- 📖 [Guía de implementación completa](GUÍA_DE_IMPLEMENTACIÓN_COMPLETA.md)
- 💡 [Ejemplos de trading mensual](GUÍA_DE_IMPLEMENTACIÓN_COMPLETA.md#ejemplos-de-uso)
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

Si este bot te resulta útil para trading mensual:

- ⭐ **Dale una estrella** a este repositorio
- 🍴 **Compártelo** con otros traders mensuales
- 🔄 **Fork** y personalízalo para tus necesidades
- 💡 **Contribuye** con mejoras al sistema MA50
- 🌟 **Reporta** resultados del bonus MA50

---

<div align="center">

**🚀 Desarrollado por [0t4c0n](https://github.com/0t4c0n)**

*"Daily monitoring, monthly trading - La consistencia supera a la perfección"*

**🌟 v2.0.0 - Monthly Trading Edition con MA50 Bonus System**

</div>