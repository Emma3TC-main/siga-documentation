# Diagramas render — DERIVADOS NO CANÓNICOS

Esta carpeta contiene copias derivadas de `../diagramas/` optimizadas para renderizado e informes.

## Uso permitido
- PlantUML local.
- Exportación PNG/SVG.
- Inserción en Word/Figma/informe.
- Sustentación.

## Uso prohibido
- Tomarlos como fuente de requisitos.
- Programar a partir de ellos.
- Alimentar agentes de IA/RAG con esta carpeta.
- Editarlos manualmente para introducir lógica.

## Fuente de verdad

Siempre: `../diagramas/**/*.puml`.

Los archivos se generan con `../tools/generar_derivados_visuales.py`.  
La paridad se verifica con `../tools/validar_fuentes_y_derivados.py`.

Las mejoras visuales reutilizan los estilos/fixes consolidados en v1.1. Para los dos diagramas nuevos de Proveedores se usa un perfil visual coherente con la familia UML v1.1.
