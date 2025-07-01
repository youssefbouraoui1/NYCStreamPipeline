import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import Components from 'unplugin-vue-components/vite'
import MotionResolver from 'motion-v/resolver'


// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(),tailwindcss(),Components({
      dts: true,
      resolvers: [
        MotionResolver()
      ],
    })],
})
