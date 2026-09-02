# ADR-004 — Schemas PostgreSQL por servicio

**Estado:** Aceptado

## Contexto
SIGA requiere consistencia, trazabilidad y viabilidad para cuatro integrantes.

## Decisión
Instancia compartida académica con ownership lógico y sin SQL cross-schema.

## Alternativas
1. Mantener la opción preliminar/simple. 2. Adoptar una alternativa más compleja/administrada. 3. Decisión seleccionada con límites.

## Justificación
Prioriza consistencia, comprensibilidad, capacidad de prueba y cronograma.

## Consecuencias
Mejora claridad y trazabilidad; exige disciplina de contratos/configuración.

## Riesgos
Complejidad operativa y necesidad de actualizar documentación si cambia.

## Revisión
Reabrir solo ante requisito verificable que la decisión actual no satisfaga razonablemente.
