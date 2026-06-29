<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { UploadFilled } from '@element-plus/icons-vue'
import {
  getAchievement, createAchievement, updateAchievement,
  getBatches, getCategories,
  ALLOWED_EXTS, MAX_FILE_SIZE, canEdit,
} from '@/api/achievements'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)

const loading = ref(false)
const batches = ref<any[]>([])
const categories = ref<any[]>([])
const form = ref({
  batch: null as number | null,
  category: null as number | null,
  title: '',
  achievement_date: '' as string | Date,
  level: '',
  description: '',
})
const fileList = ref<any[]>([])
const existingAttachment = ref('')

onMounted(async () => {
  try {
    const [bRes, cRes] = await Promise.all([getBatches({ status: 1 }), getCategories()])
    batches.value = bRes.data.data.results
    categories.value = cRes.data.data.results
  } catch { /* ignore */ }

  if (isEdit.value) {
    loading.value = true
    try {
      const res = await getAchievement(Number(route.params.id))
      const d = res.data.data
      if (!canEdit(d.status)) {
        ElMessage.warning('当前状态不允许编辑')
        router.push('/achievements')
        return
      }
      form.value = {
        batch: d.batch,
        category: d.category,
        title: d.title,
        achievement_date: d.achievement_date ? new Date(d.achievement_date) : '',
        level: d.level || '',
        description: d.description || '',
      }
      if (d.attachment_url) {
        existingAttachment.value = d.attachment_url
      }
    } finally {
      loading.value = false
    }
  }
})

function isImage(url: string) {
  return /\.(jpg|jpeg|png)$/i.test(url)
}

async function handleSubmit() {
  loading.value = true
  try {
    const fd = new FormData()
    fd.append('batch', String(form.value.batch))
    fd.append('category', String(form.value.category))
    fd.append('title', form.value.title)
    if (form.value.achievement_date) {
      const d: any = form.value.achievement_date
      const dateStr = d instanceof Date
        ? d.toISOString().split('T')[0]
        : String(d)
      fd.append('achievement_date', dateStr)
    }
    if (form.value.level) fd.append('level', form.value.level)
    if (form.value.description) fd.append('description', form.value.description)
    if (fileList.value.length > 0) {
      const f = fileList.value[0].raw
      if (f) {
        const ext = '.' + f.name.split('.').pop()?.toLowerCase()
        if (!ALLOWED_EXTS.includes(ext)) {
          ElMessage.error(`仅支持 ${ALLOWED_EXTS.join(', ')} 格式`)
          loading.value = false
          return
        }
        if (f.size > MAX_FILE_SIZE) {
          ElMessage.error('文件大小不能超过 10MB')
          loading.value = false
          return
        }
        fd.append('attachment', f)
      }
    }

    if (isEdit.value) {
      await updateAchievement(Number(route.params.id), fd)
      ElMessage.success('修改成功')
    } else {
      await createAchievement(fd)
      ElMessage.success('创建成功')
    }
    router.push('/achievements')
  } catch (err: any) {
    const msg = err.response?.data?.message || '操作失败'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

</script>

<template>
  <div v-loading="loading">
    <h2>{{ isEdit ? '编辑成果' : '新增成果' }}</h2>
    <el-form :model="form" label-width="100px" style="max-width: 600px; margin-top: 20px;">
      <el-form-item label="测评批次" required>
        <el-select v-model="form.batch" placeholder="请选择" style="width: 100%">
          <el-option v-for="b in batches" :key="b.id" :label="b.name" :value="b.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="成果分类" required>
        <el-select v-model="form.category" placeholder="请选择" style="width: 100%">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="成果名称" required>
        <el-input v-model="form.title" placeholder="例如：全国数学建模大赛一等奖" />
      </el-form-item>
      <el-form-item label="获得日期">
        <el-date-picker v-model="form.achievement_date" type="date" style="width: 100%" />
      </el-form-item>
      <el-form-item label="成果等级">
        <el-select v-model="form.level" placeholder="请选择" style="width: 100%" clearable>
          <el-option label="国家级" value="国家级" />
          <el-option label="省级" value="省级" />
          <el-option label="校级" value="校级" />
          <el-option label="院级" value="院级" />
        </el-select>
      </el-form-item>
      <el-form-item label="成果说明">
        <el-input v-model="form.description" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item label="证明材料">
        <!-- 现有附件 -->
        <div v-if="existingAttachment" style="margin-bottom:12px;padding:8px;background:#f5f7fa;border-radius:4px;">
          <span style="color:#409eff">📎 当前附件：</span>
          <template v-if="isImage(existingAttachment)">
            <el-image :src="existingAttachment" style="max-width:200px;max-height:120px;display:block;margin-top:4px" />
          </template>
          <template v-else>
            <el-link :href="existingAttachment" target="_blank">PDF预览</el-link>
          </template>
        </div>
        <div style="margin-bottom:4px;color:#909399;font-size:12px;">
          ⚠️ 请上传获奖证书、证明文件等材料，供审核老师审核
        </div>
        <el-upload
          v-model:file-list="fileList"
          :limit="1"
          :auto-upload="false"
          drag
          accept=".jpg,.jpeg,.png,.pdf"
        >
          <el-icon><UploadFilled /></el-icon>
          <div>{{ existingAttachment ? '点击替换附件（.jpg/.png/.pdf，≤10MB）' : '点击或拖拽上传证明材料（.jpg/.png/.pdf，≤10MB）' }}</div>
        </el-upload>
        <div v-if="existingAttachment && fileList.length === 0" style="margin-top:4px;color:#909399;">未选择新文件则保留原附件</div>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          {{ isEdit ? '保存修改' : '保存草稿' }}
        </el-button>
        <el-button @click="router.push('/achievements')">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
