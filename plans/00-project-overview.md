# Mobile Ad Automation System - Project Overview

## 🎯 Project Goal

Build a Python-based system to automate mobile game ad interactions using Appium on real Android devices. The system will:

1. **Collect training data** by capturing screenshots and metadata during ad viewing sessions
2. **Train YOLO-based object detection models** to identify ad UI elements (close buttons, skip buttons, etc.)
3. **Autonomously navigate ads** using trained models while continuing to collect data for improvement
4. **Iterate continuously** through a feedback loop: data collection → training → inference → more data collection

## 🎓 Use Case

Mobile games offer rewards (coins, lives, etc.) for watching advertisements. These ads typically require multiple user interactions to dismiss. This system aims to:

- Automate the tedious process of watching and dismissing ads
- Learn to recognize ad UI patterns across different ad networks
- Achieve 90% success rate in ad navigation
- Serve as a plug-and-play component for mobile game bots

## 🏆 Success Criteria

### Primary Goals
- **Model inference time**: < 2 seconds on MacBook CPU
- **Ad navigation success rate**: > 90% (final goal)
- **Multi-device support**: Run on 2+ Android devices simultaneously
- **Multi-game support**: Work across 3-5 different mobile games

### Secondary Goals
- Minimize manual annotation effort through model-assisted labeling
- Maintain clean separation between data collection engine and ad navigation intelligence (submodule)
- Build presentation-worthy materials documenting the journey from first model to production-ready system

## 📊 Project Type

**Research & Learning Project** with practical output
- No production deployment constraints
- No timeline pressure
- Focus on experimentation and iterative improvement
- Presentation-ready documentation for future talks

## 🔄 Development Philosophy

- **Incremental approach**: Build MVP first, add complexity gradually
- **Data-driven**: Let session data guide model improvements
- **Fail-safe design**: Isolate device failures, never delete raw data
- **Human-in-the-loop**: Manual review of model predictions before training
- **Configurable everything**: Make thresholds, intervals, and parameters easy to adjust

## 🎨 Key Design Principles

1. **Never delete session data**: Raw session folders are immutable once created
2. **Device independence**: Each device runs autonomous sessions, failures don't propagate
3. **Post-hoc filtering**: Capture all frames continuously, filter intelligently later
4. **Clean boundaries**: Parent repo handles Android/Appium, submodule handles ML/decisions
5. **Git-friendly**: Sessions and models are local-only, configs are version-controlled

## 🧩 System Components

### Parent Repository: `automate-mobile-applications`
Handles device coordination, Appium automation, session management, data collection

### Submodule: `libs/mobile-game-ad-detection`
Contains all ML intelligence: model training, inference, decision-making logic

## 📈 Milestones

1. **Data Collection MVP** (Phase 1): Capture 50+ raw sessions
2. **First Model** (Phase 3): Train YOLO model on 100-200 manually annotated images
3. **Autonomous Navigation** (Phase 4): Achieve >50% success rate with first model
4. **Production Ready** (Phase 5): Achieve >90% success rate, multi-game support

## 🔗 Related Documents

- [Architecture & Data Schemas](./01-architecture-and-schemas.md)
- [Phase 1: Data Collection](./02-phase-1-data-collection.md)
- [Phase 2: Filtering](./03-phase-2-filtering.md)
- [Phase 3: Model Training](./04-phase-3-training.md)
- [Phase 4: Inference](./05-phase-4-inference.md)
- [Phase 5: Iteration](./06-phase-5-iteration.md)
- [Technical Stack](./07-technical-stack.md)
- [Implementation Workflows](./08-workflows.md)
- [Challenges & Mitigations](./09-challenges.md)

## 📅 Status

**Current Phase**: Planning Complete ✅  
**Next Step**: Begin Phase 1 implementation - Project setup and configuration system

---

**Last Updated**: 2025-11-02  
**Project Lead**: Kevin Vosburgh
